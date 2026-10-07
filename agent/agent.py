"""The Agent: request -> route -> resolve inputs -> execute workflow -> structured response."""
from __future__ import annotations

import uuid
from pathlib import Path

from .config import Config
from .engine import WorkflowEngine
from .errors import WorkflowConfigError
from .excel_loader import load_workflows, validate_workflows
from .input_resolver import resolve_inputs
from .llm import get_llm
from .models import AgentResponse, Routing
from .router import Router
from .run_logger import RunLogger


class Agent:
    def __init__(self, config: Config | None = None, llm=None, workbook_path: Path | None = None):
        self.config = config or Config()
        if workbook_path:
            self.config.workbook_path = Path(workbook_path)
        self.llm = llm if llm is not None else get_llm()
        self.workflows = load_workflows(self.config.workbook_path)
        problems = validate_workflows(self.workflows)
        if problems:
            raise WorkflowConfigError("Workflow workbook has problems:\n  - " + "\n  - ".join(problems))
        self.router = Router(self.workflows, self.llm, self.config.router_min_confidence)
        self.engine = WorkflowEngine(self.llm, self.config, self.workflows)
        self.logger = RunLogger(self.config.logs_dir / "runtime_logs.csv", self.config.log_runs)

    def run(self, request: str, params: dict | None = None, workflow_id: str | None = None) -> AgentResponse:
        run_id = "run-" + uuid.uuid4().hex[:8]
        resp = AgentResponse(request=request, status="failed", run_id=run_id, llm_mode=self.llm.name)

        # 1. identify the workflow --------------------------------------------------
        if workflow_id:
            if workflow_id not in self.workflows:
                resp.error = f"Unknown workflow id '{workflow_id}'"
                return resp
            resp.routing = Routing(workflow_id, 1.0, "explicit", "Workflow chosen explicitly by the caller")
        else:
            resp.routing = self.router.route(request)
            workflow_id = resp.routing.workflow_id
        if not workflow_id:
            resp.status = "clarify"
            opts = [f"  {i + 1}. {self.workflows[w].name} ({w}) - e.g. \"{(self.workflows[w].examples or [''])[0]}\""
                    for i, (w, _) in enumerate(resp.routing.alternatives)]
            resp.message = ("I couldn't confidently match your request to a workflow. Did you mean one of these?\n"
                            + "\n".join(opts) + "\nRephrase your request or pick one.")
            resp.missing = [{"name": "workflow", "ask": "Which workflow do you want?"}]
            return resp
        wf = self.workflows[workflow_id]
        resp.workflow_id, resp.workflow_name = wf.id, wf.name

        # 2. gather + validate inputs (ask the user for anything required and missing) ---
        inputs, sources, missing = resolve_inputs(wf, request, params, self.llm, self.config)
        resp.inputs, resp.input_sources = inputs, sources
        if missing:
            resp.status, resp.missing = "needs_input", missing
            resp.message = "Before I can run this workflow I need:\n" + "\n".join(f"  - {m['ask']}" for m in missing)
            return resp

        # 3. execute ---------------------------------------------------------------
        ex = self.engine.execute(wf, inputs, run_id)
        resp.steps, resp.decisions = ex.trace, ex.decisions
        resp.status, resp.result, resp.message, resp.missing, resp.error = ex.status, ex.result, ex.message, ex.missing, ex.error
        self.logger.log(run_id, wf.id, ex.trace)
        return resp
