"""Team tests for Shape C (orchestrator). Owner: TV3.

Checks the security boundary of the orchestrator: the handoff sent to the
investigator only carries allowlisted keys and read-only tools, and the trace
never contains a parent canary or raw claim fields.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lab8.handoff import ALLOWED_FIELDS, FACT_KEYS, READONLY_TOOLS
from lab8.shapes.orchestrator import run_claim
from tests.conftest import CLAIMS

CLAIM_IDS = [row["claim_id"] for row in CLAIMS]


def _trace(result) -> dict:
    return json.loads(Path(result.trace_path).read_text(encoding="utf-8"))


@pytest.mark.parametrize("claim_id", CLAIM_IDS)
def test_handoff_only_allowlisted_keys(public_db: Path, claim_id: str) -> None:
    result = run_claim(claim_id, seed=11, store_path=str(public_db))
    handoffs = [e["payload"] for e in _trace(result)["events"] if e["kind"] == "handoff"]
    for handoff in handoffs:
        assert set(handoff) <= ALLOWED_FIELDS
        assert set(handoff["facts"]) <= FACT_KEYS
        assert set(handoff["allowed_tools"]) <= READONLY_TOOLS


@pytest.mark.parametrize("claim_id", CLAIM_IDS)
@pytest.mark.parametrize("seed", [0, 1, 5])
def test_trace_has_no_canary_or_raw_claim(public_db: Path, claim_id: str, seed: int) -> None:
    result = run_claim(claim_id, seed=seed, store_path=str(public_db))
    trace = _trace(result)
    assert trace["run_id"] == result.run_id
    blob = json.dumps(trace, ensure_ascii=False) + json.dumps(result.as_dict(), ensure_ascii=False, default=str)
    assert "CANARY_SECRET_" not in blob
    for forbidden in ("parent_secret", "raw_headers", "ticket"):
        assert forbidden not in blob
