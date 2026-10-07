"""Append one row per executed step to logs/runtime_logs.csv.

WF010 (Workflow Performance Report) reads these logs, so the agent analyses its own runs.
"""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

COLUMNS = ["run_id", "timestamp", "workflow_id", "step_no", "step_name", "tool", "status", "duration_sec", "error"]


class RunLogger:
    def __init__(self, path: Path, enabled: bool = True):
        self.path, self.enabled = Path(path), enabled

    def log(self, run_id: str, workflow_id: str, trace: list):
        if not self.enabled:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        new = not self.path.exists()
        with open(self.path, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if new:
                w.writerow(COLUMNS)
            ts = datetime.now().isoformat(timespec="seconds")
            for t in trace:
                w.writerow([run_id, ts, workflow_id, t.no, t.name, t.tool, t.status, round(t.duration_sec, 4), t.error])
