from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app.backtest import run_example


def test_run_example_generates_equity_curve():
    result = run_example()
    assert len(result.equity_curve) > 0
    assert isinstance(result.logs, list)
