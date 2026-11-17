"""Shape A — deterministic workflow. Student work.

Signature (do not change):

    run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult

Suggested steps. Money stays in code (`lab8.tools.compute_compensation`).

1. Open the store. Read the claim through `get_claim_view` (not SELECT *).
2. Missing order_id -> status `needs_info`. Do not write the ledger.
3. `lookup_order`. If not visible -> `escalated`. Do not copy phone, address, item, internal note.
4. Quote from the order row. Ignore delay numbers written in the ticket.
5. Quote amount 0 -> `denied`. Do not call issue_refund.
6. Quote amount > 0 -> `durability.issue_refund(conn, claim_id, <full quote>)`.
   Pass the FULL quote. The host checks the claim's own approval and subtracts
   what earlier claims already got for the same order (T13, T14). Do not
   subtract it yourself or the host subtracts twice.
   Auth failure or order already refunded -> `denied` (the host writes `policy_denied`).
   `proposal_amount` stays the full quote. Amount conflict -> `failed`.
7. Success -> `resolved`. One ledger row, one `refund_committed` audit.
8. Use MockLLM only to draft the reply text, if you want a model call at all.

The model must not choose the refund amount and must not commit the refund.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.

Implementation notes (team):
- The ticket text is never parsed for numbers and never written to the trace.
  It is user data, not an instruction ("ignore policy" has no effect here).
- The trace records only: the claim id/order id/status flags, the allowlisted
  order view returned by `lookup_order`, the quote, and the host outcome.
  It never records the claim row, `principal_id`, the ticket, or the reply text.
- The only model call is the reply draft, made after the amount is fixed.
"""

from __future__ import annotations

import sqlite3

from lab8 import durability
from lab8.db import connect
from lab8.mock_llm import complete
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.tools import compute_compensation, get_claim_view, lookup_order, tool_cost
from lab8.trace import Trace

SHAPE = "workflow"


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

    def done(status: str, proposal: int, reason: str | None) -> RunResult:
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

    # Step 1: allowlisted claim view. The ticket stays out of the trace.
    budget.add_tool(tool_cost())
    claim = get_claim_view(conn, claim_id)
    if not claim["found"]:
        trace.add("claim", {"claim_id": claim_id, "found": False})
        return done("failed", 0, "unknown_claim")
    order_id = claim["order_id"]
    trace.add("claim", {"claim_id": claim_id, "found": True, "has_order_id": bool(order_id)})

    # Step 2: no order id -> ask the customer, never touch the ledger.
    if not order_id:
        _draft(budget, seed, "needs_info")
        return done("needs_info", 0, "missing_order_id")

    # Step 3: order lookup scoped to the claimant. Only allowlisted fields come back.
    budget.add_tool(tool_cost())
    order_view = lookup_order(conn, order_id, claim["principal_id"])
    if not order_view["visible"]:
        trace.add("lookup_order", {"visible": False, "reason": order_view["reason"]})
        _draft(budget, seed, "escalated")
        return done("escalated", 0, order_view["reason"])
    trace.add("lookup_order", safe_dump(order_view))

    # Step 4: quote from the order row and current policy only.
    budget.add_tool(tool_cost())
    quote = compute_compensation(conn, order_view["order"])
    proposal = int(quote["amount_vnd"])
    trace.add("quote", safe_dump(quote))

    # Step 5: nothing owed -> deny in code, no host call, no policy_denied audit.
    if proposal <= 0:
        _draft(budget, seed, "denied")
        return done("denied", 0, quote.get("reason"))

    # Step 6: the host is the only writer. Full quote; crash_at passes through and
    # InjectedCrash is deliberately not caught so the crash suite can resume.
    try:
        outcome = durability.issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except durability.InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise
    trace.add(
        "issue_refund",
        {"ok": bool(outcome.get("ok")), "conflict": bool(outcome.get("conflict")), "reason": outcome.get("reason")},
    )

    if not outcome["ok"]:
        status = "failed" if outcome.get("conflict") else "denied"
        _draft(budget, seed, status)
        return done(status, proposal, outcome.get("reason"))

    # Step 7/8: committed. The model only drafts the reply, after the money is fixed.
    _draft(budget, seed, "resolved")
    return done("resolved", proposal, None)


def _draft(budget: Budget, seed: int, status: str) -> None:
    """Reply text only. Not stored in the trace, not used for any decision."""
    complete(budget, seed=seed, purpose="draft", prompt=f"status={status}")
