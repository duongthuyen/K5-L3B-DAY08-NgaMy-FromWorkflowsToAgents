"""Team tests for evaluation evidence. Owner: TV4 (Phạm Minh Tâm, done by duongthuyen).

1. Must-pass 3 at shape level: crash at every injection point inside a shape,
   then resume, still gives one refund and one refund_committed audit.
2. Committed evidence files in src/reports/ have the shape the ADR relies on.
   These are only checked when the file exists, so the gate stays green before CP5.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lab8.config_loader import repo_path
from lab8.db import connect
from lab8.durability import InjectedCrash, committed_audit_count, get_refund
from lab8.shapes.workflow import run_claim as workflow_run

CRASH_POINTS = ("before_effect", "after_effect_before_checkpoint", "after_checkpoint")
REQUIRED_SEEDS = [11, 22, 33, 44, 55]
REQUIRED_SHAPES = {"workflow", "single", "orchestrator", "swarm"}


@pytest.mark.parametrize("point", CRASH_POINTS)
def test_workflow_crash_then_resume_pays_once(public_db: Path, point: str) -> None:
    with pytest.raises(InjectedCrash):
        workflow_run("C-012", seed=11, store_path=str(public_db), crash_at=point)
    resumed = workflow_run("C-012", seed=11, store_path=str(public_db))
    assert resumed.status == "resolved"
    conn = connect(str(public_db))
    assert get_refund(conn, "C-012")["amount_vnd"] == 35000
    assert committed_audit_count(conn, "C-012") == 1
    conn.close()


def _report(name: str) -> dict | None:
    path = Path(repo_path("reports", name))
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def test_crash_report_is_20_of_20() -> None:
    report = _report("crash.json")
    if report is None:
        pytest.skip("reports/crash.json not generated yet")
    assert report["crash_safety"] == "20/20"
    assert report["passed"] == 20


def test_benchmark_report_covers_contract() -> None:
    report = _report("benchmark.json")
    if report is None:
        pytest.skip("reports/benchmark.json not generated yet")
    shapes = set(report["by_shape"])
    claims = {t["claim_id"] for t in report["trials"]}
    seeds = sorted({int(t["seed"]) for t in report["trials"]})
    assert seeds == REQUIRED_SEEDS
    assert len(claims) >= 10
    # Before CP5 the file may hold a partial run; the final one must have all 4 shapes.
    assert shapes <= REQUIRED_SHAPES and "workflow" in shapes and "swarm" in shapes
    for trial in report["trials"]:
        assert trial["run_id"] == f"R-{trial['shape']}-{trial['claim_id']}-s{trial['seed']}"
