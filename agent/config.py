from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

try:  # optional
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except Exception:  # pragma: no cover
    pass


@dataclass
class Config:
    root: Path = ROOT
    workbook_path: Path = field(default_factory=lambda: ROOT / "workflows" / "ai_agent_workflows.xlsx")
    outputs_dir: Path = field(default_factory=lambda: ROOT / "outputs")
    logs_dir: Path = field(default_factory=lambda: ROOT / "logs")
    # router: below this confidence (or tiny margin) the agent asks the user to pick a workflow
    router_min_confidence: float = float(os.getenv("ROUTER_MIN_CONFIDENCE", "0.35"))
    retry_backoff_sec: float = float(os.getenv("RETRY_BACKOFF_SEC", "0.05"))
    log_runs: bool = os.getenv("LOG_RUNS", "1") != "0"

    def __post_init__(self):
        self.outputs_dir = Path(self.outputs_dir)
        self.logs_dir = Path(self.logs_dir)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def resolve_path(self, p) -> Path:
        p = Path(str(p)).expanduser()
        return p if p.is_absolute() else self.root / p
