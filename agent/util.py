"""Shared helpers: file IO, number/date parsing, text normalisation."""
from __future__ import annotations

import csv
import re
from datetime import date, datetime, timedelta
from pathlib import Path

from dateutil import parser as dtparser

from .errors import ToolError

STOPWORDS = {"a", "an", "the", "of", "for", "to", "and", "or", "in", "on", "at", "by", "with", "is", "are", "be",
             "this", "that", "these", "those", "me", "my", "our", "us", "we", "i", "it", "any", "all", "from",
             "please", "can", "could", "you", "show", "give", "get", "which", "what", "who", "how", "do", "does",
             "now", "today", "need", "needs", "find", "check", "tell", "list"}


def stem(w: str) -> str:
    for suf in ("ings", "ing", "ies", "ed", "es", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            return w[: -len(suf)] + ("y" if suf == "ies" else "")
    return w


def tokenize(text: str, drop_stop: bool = True) -> list[str]:
    toks = re.findall(r"[a-z0-9]+", str(text).lower())
    if drop_stop:
        toks = [t for t in toks if t not in STOPWORDS]
    return [stem(t) for t in toks]


def norm_header(h) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(h).strip().lower()).strip("_")


def norm_key(s) -> str:
    """Normalise identifiers (SKUs): upper-case, alphanumerics only."""
    return re.sub(r"[^A-Z0-9]", "", str(s or "").upper())


def to_number(v):
    """'$1,234.50' -> 1234.5 ; '12%' -> 12.0 ; '' -> None ; raises ValueError for junk."""
    if v is None:
        return None
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return v
    s = str(v).strip()
    if s == "":
        return None
    s = re.sub(r"[,$€£₹%\s]", "", s)
    if not re.fullmatch(r"-?\d+(\.\d+)?", s):
        raise ValueError(f"not a number: {v!r}")
    f = float(s)
    return int(f) if f.is_integer() and "." not in s else f


def read_table(path: Path, sheet: str | None = None):
    """Read CSV / XLSX into (rows, columns). Row dicts carry '_row' = source row number."""
    path = Path(path)
    if not path.exists():
        raise ToolError(f"File not found: {path}")
    suffix = path.suffix.lower()
    rows, columns = [], []
    try:
        if suffix in (".xlsx", ".xlsm", ".xls"):
            import openpyxl
            wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
            ws = wb[sheet] if sheet else wb[wb.sheetnames[0]]
            it = ws.iter_rows(values_only=True)
            header = next(it, None)
            if header is None:
                raise ToolError(f"{path.name} is empty")
            columns = [str(h).strip() if h is not None else "" for h in header]
            for i, r in enumerate(it, start=2):
                if r is None or all(c is None or str(c).strip() == "" for c in r):
                    continue
                d = {columns[j]: ("" if r[j] is None else r[j]) for j in range(len(columns)) if columns[j]}
                d["_row"] = i
                rows.append(d)
        elif suffix in (".csv", ".txt", ".tsv"):
            raw = path.read_bytes()
            try:
                text = raw.decode("utf-8-sig")
            except UnicodeDecodeError:
                text = raw.decode("latin-1")
            reader = csv.reader(text.splitlines(), delimiter="\t" if suffix == ".tsv" else ",")
            header = next(reader, None)
            if not header:
                raise ToolError(f"{path.name} is empty")
            columns = [h.strip() for h in header]
            for i, r in enumerate(reader, start=2):
                if not r or all(c.strip() == "" for c in r):
                    continue
                d = {columns[j]: (r[j].strip() if j < len(r) else "") for j in range(len(columns)) if columns[j]}
                d["_row"] = i
                rows.append(d)
        else:
            raise ToolError(f"Unsupported file type '{suffix}' for {path.name} (use .csv or .xlsx)")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError(f"Could not read {path.name}: {e}") from e
    return rows, [c for c in columns if c]


def write_csv(rows: list[dict], path: Path, columns: list[str] | None = None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [{k: v for k, v in r.items() if not str(k).startswith("_")} for r in rows]
    if columns is None:
        columns = []
        for r in rows:
            for k in r:
                if k not in columns:
                    columns.append(k)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    return path


_MONTHS = r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
_DATE_PATTERNS = [
    r"\d{4}-\d{2}-\d{2}",
    rf"\d{{1,2}}(?:st|nd|rd|th)?\s+{_MONTHS}\.?,?\s+\d{{4}}",
    rf"{_MONTHS}\.?\s+\d{{1,2}}(?:st|nd|rd|th)?,?\s+\d{{4}}",
    r"\d{1,2}/\d{1,2}/\d{4}",
]
_DATE_RE = re.compile("|".join(f"(?:{p})" for p in _DATE_PATTERNS), re.I)


def find_dates(text: str) -> list[date]:
    out = []
    for m in _DATE_RE.finditer(str(text)):
        raw = m.group(0)
        try:
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):          # ISO: never let dateutil reinterpret it
                out.append(date.fromisoformat(raw))
            else:                                                 # dd/mm/yyyy (day-first) and written-out months
                out.append(dtparser.parse(re.sub(r"(st|nd|rd|th)\b", "", raw, flags=re.I), dayfirst=True).date())
        except (ValueError, OverflowError):
            continue
    return out


def parse_date_range(text) -> dict | None:
    if isinstance(text, dict) and text.get("start") and text.get("end"):
        return {"start": str(text["start"]), "end": str(text["end"])}
    ds = find_dates(text)
    if len(ds) >= 2:
        a, b = ds[0], ds[1]
        return {"start": a.isoformat(), "end": b.isoformat()}
    return None


_WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def parse_deadline(text: str, today: date | None = None) -> date | None:
    """ISO / 'Oct 12 2026' dates, 'today', 'tomorrow', 'by friday', 'in 3 days', 'next week'."""
    today = today or date.today()
    t = str(text).lower()
    ds = find_dates(t)
    if ds:
        return ds[0]
    if "today" in t or "eod" in t:
        return today
    if "tomorrow" in t:
        return today + timedelta(days=1)
    m = re.search(r"in\s+(\d+)\s+days?", t)
    if m:
        return today + timedelta(days=int(m.group(1)))
    if "next week" in t:
        return today + timedelta(days=7)
    for i, d in enumerate(_WEEKDAYS):
        if re.search(rf"\b{d}\b", t):
            delta = (i - today.weekday()) % 7 or 7
            return today + timedelta(days=delta)
    return None
