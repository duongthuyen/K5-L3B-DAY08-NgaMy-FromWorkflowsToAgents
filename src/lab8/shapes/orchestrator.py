"""Shape C — orchestrator plus read-only investigators. Student work.

1. Build a handoff with `lab8.handoff.make_handoff`. Allowed tools are read-only.
   Never put parent_secret, raw headers, or the full claim row into facts.
2. `lab8.runtime.run_readonly_investigators` runs those tools.
3. The orchestrator quotes from the investigator's order view and calls
   `durability.issue_refund`. Investigators have no write registry.
   Pass the full quote; the host subtracts earlier refunds on the same order.
   `lookup_refund_history` is a read-only tool you may hand to an investigator.
4. Trace the sanitized handoff, not the parent context.

An LLM summary of the parent context is not a sanitizer. Use the allowlist.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.

Ranh giới code / model trong shape này:
- Model (MockLLM) chỉ soạn chữ (purpose="parse"/"draft"). Không số nào từ model
  được dùng để tính tiền.
- Số tiền do `compute_compensation` tính trên order row từ DB (qua investigator).
  Delay ghi trong ticket bị bỏ qua: ticket là dữ liệu người dùng, không phải lệnh.
- Chỉ orchestrator gọi `issue_refund`, với quote đầy đủ; host trừ phần đã hoàn.
- Trace chỉ ghi handoff đã sanitize và các field đã qua allowlist, không ghi
  claim row (có parent_secret) hay ticket.
"""

from __future__ import annotations

import sqlite3

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.handoff import make_handoff
from lab8.mock_llm import complete
from lab8.runtime import run_readonly_investigators
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.tools import tool_cost
from lab8.trace import Trace

SHAPE = "orchestrator"
INVESTIGATOR_TOOLS = ["lookup_order", "lookup_policy", "lookup_refund_history", "compute_compensation"]


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    conn = connect(store_path)
    try:
        return _run(conn, claim_id, seed=seed, crash_at=crash_at)
    finally:
        conn.close()


def _run(conn: sqlite3.Connection, claim_id: str, *, seed: int, crash_at: str | None) -> RunResult:
    budget = Budget()
    trace = Trace(make_run_id(SHAPE, claim_id, seed))

    def done(status: str, proposal: int = 0, reason: str | None = None) -> RunResult:
        trace.add("decision", {"status": status, "proposal_amount": int(proposal), "reason": reason})
        return finish(
            conn,
            shape=SHAPE,
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
            error_reason=reason,
        )

    # Orchestrator đọc claim row trong code; row này KHÔNG vào trace hay handoff.
    budget.add_tool(tool_cost())
    claim_row = conn.execute(
        "SELECT claim_id, principal_id, order_id, ticket FROM claims WHERE claim_id = ?",
        (claim_id,),
    ).fetchone()
    if claim_row is None:
        return done("failed", reason="unknown_claim")

    # Model chỉ đọc ticket để soạn chữ; kết quả không dùng cho số tiền.
    complete(budget, seed=seed, purpose="parse", prompt=claim_row["ticket"])

    if not claim_row["order_id"]:
        complete(budget, seed=seed, purpose="draft", prompt="needs_info")
        return done("needs_info", reason="missing_order_id")

    handoff = make_handoff(
        request_id=f"REQ-{claim_id}",
        claim_id=claim_id,
        task="check_applicable_policy",
        facts={},
        allowed_tools=INVESTIGATOR_TOOLS,
    )
    trace.add("handoff", safe_dump(handoff))

    investigated = run_readonly_investigators(conn, budget, handoff, principal_id=claim_row["principal_id"])
    tools = investigated["tools"]
    order_view = tools.get("lookup_order") or {}
    history = tools.get("lookup_refund_history") or {}
    trace.add(
        "investigator",
        {
            "claim_view": investigated["claim_view"],
            "order_visible": bool(order_view.get("visible")),
            "order_reason": order_view.get("reason"),
            "policy_count": len((tools.get("lookup_policy") or {}).get("policies") or []),
            "prior_refund_count": len(history.get("refunds") or []) if isinstance(history, dict) else 0,
        },
    )

    if not order_view.get("visible"):
        complete(budget, seed=seed, purpose="draft", prompt="escalated")
        return done("escalated", reason=order_view.get("reason"))

    quote = tools.get("compute_compensation") or {}
    proposal = int(quote.get("amount_vnd") or 0)
    trace.add("quote", {"amount_vnd": proposal, "reason": quote.get("reason")})
    complete(budget, seed=seed, purpose="draft", prompt=f"proposal={proposal}")

    if proposal <= 0:
        return done("denied", reason=quote.get("reason"))

    # CP3: crash_at đi thẳng vào host; không nuốt InjectedCrash.
    try:
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise

    if not outcome["ok"]:
        return done("failed" if outcome["conflict"] else "denied", proposal, outcome["reason"])
    return done("resolved", proposal)
