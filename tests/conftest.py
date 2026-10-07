import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent import Agent, Config  # noqa: E402
from agent.llm import NullLLM  # noqa: E402
from agent.tools.orders import reset_simulation  # noqa: E402


@pytest.fixture
def make_agent(tmp_path):
    def _make(llm=None, workbook=None):
        reset_simulation()
        cfg = Config(outputs_dir=tmp_path / "out", logs_dir=tmp_path / "logs")
        a = Agent(cfg, llm=llm or NullLLM(), workbook_path=workbook)
        return a
    return _make


@pytest.fixture
def agent(make_agent):
    return make_agent()


def tables(resp):
    return {t["name"]: t for t in resp.result["tables"]}
