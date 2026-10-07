"""Workflow selection.

Primary  : LLM *tool call* ``select_workflow`` over a catalog generated from the Excel sheet.
Fallback : deterministic TF-IDF cosine similarity (offline, no API key, also used when the LLM
           errors out or returns an unknown workflow id).
Either way: low confidence => the agent asks a clarifying question instead of guessing.
"""
from __future__ import annotations

import math
from collections import Counter

from .errors import LLMError
from .models import Routing
from .util import tokenize


def _catalog_text(wfs: dict) -> str:
    lines = []
    for wf in wfs.values():
        lines.append(f"- {wf.id}: {wf.name}\n    trigger: {wf.trigger}\n    inputs: {wf.inputs_text}\n"
                     f"    output: {wf.expected_output}\n    example requests: {' | '.join(wf.examples)}")
    return "\n".join(lines)


class LexicalRouter:
    def __init__(self, wfs: dict):
        self.wfs = wfs
        self.docs: dict[str, Counter] = {}
        for wf in wfs.values():
            c = Counter()
            for text, w in ((wf.name, 4), (wf.keywords, 4), (wf.trigger, 2), (wf.expected_output, 1),
                            (wf.steps_text, 1), (wf.inputs_text, 1)):
                for t in tokenize(text):
                    c[t] += w
            self.docs[wf.id] = c
        n = len(self.docs)
        df = Counter(t for c in self.docs.values() for t in c)
        self.idf = {t: math.log((1 + n) / (1 + d)) + 1 for t, d in df.items()}
        self.vecs = {i: self._vec(c) for i, c in self.docs.items()}

    def _vec(self, counts: Counter):
        v = {t: (1 + math.log(tf)) * self.idf.get(t, 1.0) for t, tf in counts.items()}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        return {t: x / norm for t, x in v.items()}

    def rank(self, request: str):
        q = self._vec(Counter(t for t in tokenize(request) if t in self.idf))
        scores = [(i, sum(w * v.get(t, 0.0) for t, w in q.items())) for i, v in self.vecs.items()]
        return sorted(scores, key=lambda x: -x[1])


class Router:
    def __init__(self, wfs: dict, llm, min_confidence: float = 0.35):
        self.wfs, self.llm, self.min_conf = wfs, llm, min_confidence
        self.lexical = LexicalRouter(wfs)

    def route(self, request: str) -> Routing:
        if self.llm.available:
            try:
                r = self._llm_route(request)
                if r:
                    return r
            except LLMError as e:
                fallback_note = f"(LLM routing failed: {e}; used keyword router) "
                r = self._lexical_route(request)
                r.reasoning = fallback_note + r.reasoning
                return r
        return self._lexical_route(request)

    # -- LLM tool call ---------------------------------------------------------------
    def _llm_route(self, request: str) -> Routing | None:
        ids = list(self.wfs) + ["NONE"]
        schema = {"type": "object", "properties": {
            "workflow_id": {"type": "string", "enum": ids},
            "confidence": {"type": "number", "description": "0..1"},
            "reasoning": {"type": "string", "description": "one sentence"}},
            "required": ["workflow_id", "confidence", "reasoning"]}
        system = ("You are the routing layer of a business-workflow agent. Pick the single workflow that best "
                  "matches the user's request, or NONE if nothing fits. Do not answer the request itself.\n\n"
                  "Available workflows:\n" + _catalog_text(self.wfs))
        out = self.llm.structured(system, f"User request: {request}", "select_workflow",
                                  "Select the workflow that should handle the request", schema)
        wid = out.get("workflow_id")
        if wid not in ids:
            raise LLMError(f"LLM returned unknown workflow id {wid!r}")
        conf = float(out.get("confidence", 0))
        alts = [(i, round(s, 3)) for i, s in self.lexical.rank(request)[:3]]
        if wid == "NONE" or conf < self.min_conf:
            return Routing(None, conf, "llm-tool-call", out.get("reasoning", ""), alts)
        return Routing(wid, conf, "llm-tool-call", out.get("reasoning", ""), alts)

    # -- deterministic fallback -------------------------------------------------------
    def _lexical_route(self, request: str) -> Routing:
        ranked = self.lexical.rank(request)
        (top, s1), (_, s2) = ranked[0], ranked[1]
        if s1 <= 0:
            return Routing(None, 0.0, "keyword-tfidf", "No keywords in the request matched any workflow", ranked[:3])
        margin = (s1 - s2) / s1
        conf = round(0.5 * min(1.0, s1 / 0.25) + 0.5 * margin, 2)
        alts = [(i, round(s, 3)) for i, s in ranked[:3]]
        name = self.wfs[top].name
        why = f"Best keyword/TF-IDF match with '{name}' (score {s1:.2f}, runner-up {s2:.2f})"
        if conf < self.min_conf:
            return Routing(None, conf, "keyword-tfidf", why + " but confidence is too low to act on", alts)
        return Routing(top, conf, "keyword-tfidf", why, alts)
