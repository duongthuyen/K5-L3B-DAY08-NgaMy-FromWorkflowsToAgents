"""Shape B — one ReAct agent. Student work.

Use `lab8.runtime.run_react` with max_steps=8. `decide` may pick a read tool.
It must not call `issue_refund`. After the loop, the host validates the quote
and is the only writer.

A decide() that trusts ticket text over the order row will fail hidden claims
where the customer overstates the delay or cites a superseded clause.

Per-order cap: an order may already have been refunded by an earlier claim.
The read tool `lookup_refund_history` shows how much. The host still enforces
the cap, so pass the full quote to `durability.issue_refund`, not a net amount.

Caps: stop at 8 steps. Count model calls in the Budget so cost stays comparable.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.

Implementation notes (team, TV2):
- `run_react` only hands `decide` the LAST tool result, so the agent keeps its
  own scratchpad (`memory`) across steps.
- Every step costs one MockLLM call (purpose="react"), so model calls are
  counted. The prompt holds only the step number and the last tool name: the
  ticket never reaches the model or the trace, so text like "ignore policy"
  or "tre 10 ngay" has no effect.
- `decide` only picks read tools: get_claim_view -> lookup_order ->
  lookup_refund_history -> compute_compensation -> final. The amount comes from
  the `compute_compensation` tool result held in memory, not from the model's
  final answer. After the loop, code (not the model) calls the host.
- The trace records tool names plus allowlisted views only. It never stores the
  claim row, `principal_id`, the ticket, or the reply text.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from lab8 import durability
from lab8.db import connect
from lab8.mock_llm import complete
from lab8.runtime import run_react
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.trace import Trace

SHAPE = "single"
MAX_STEPS = 8


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

    # --- ReAct loop: the agent only reads. ---------------------------------
    memory: dict[str, Any] = {"claim_id": claim_id, "step": 0}
    decide = _make_decide(memory, budget, seed, trace)
    loop = run_react(
        conn,
        budget,
        observation={"claim": {"claim_id": claim_id}},
        decide=decide,
        max_steps=MAX_STEPS,
    )
    final = loop["final"]
    trace.add("react_stop", {"stopped": loop["stopped"], "steps": memory["step"]})

    status = final.get("status", "failed")
    reason = final.get("error_reason")

    # Early outcomes chosen by the agent: no ledger write.
    if loop["stopped"] != "final" or status in ("failed", "needs_info", "escalated"):
        _draft(budget, seed, status)
        return done(status, 0, reason)

    # --- Code checks the agent's work before any money moves. ---------------
    # The amount comes from the compute_compensation tool result, never from
    # the model's text. If the agent finished without a quote, fail closed.
    quote = memory.get("quote")
    if quote is None:
        _draft(budget, seed, "failed")
        return done("failed", 0, "no_quote")
    proposal = int(quote["amount_vnd"])

    if proposal <= 0:
        _draft(budget, seed, "denied")
        return done("denied", 0, quote.get("reason"))

    # Host is the only writer. Full quote (host subtracts earlier refunds on
    # the same order). InjectedCrash is not swallowed: flush trace, re-raise.
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

    _draft(budget, seed, "resolved")
    return done("resolved", proposal, None)


def _make_decide(memory: dict[str, Any], budget: Budget, seed: int, trace: Trace):
    """Build the agent's decide() with a scratchpad that survives across steps."""

    def decide(seen: dict[str, Any]) -> dict[str, Any]:
        memory["step"] += 1
        last_tool = seen.get("last_tool")
        result = seen.get("last_result") or {}

        # "Think": one model call per step. No ticket text in the prompt.
        complete(budget, seed=seed, purpose="react", prompt=f"step={memory['step']} last={last_tool}")

        # Observe: store what the last read tool returned.
        if last_tool == "get_claim_view":
            if not result.get("found"):
                trace.add("claim", {"claim_id": memory["claim_id"], "found": False})
                return {"final": {"status": "failed", "error_reason": "unknown_claim"}}
            memory["order_id"] = result.get("order_id")
            memory["principal_id"] = result.get("principal_id")  # kept in memory only, not traced
            trace.add("claim", {"claim_id": memory["claim_id"], "found": True, "has_order_id": bool(memory["order_id"])})
            if not memory["order_id"]:
                return {"final": {"status": "needs_info", "error_reason": "missing_order_id"}}
        elif last_tool == "lookup_order":
            if not result.get("visible"):
                trace.add("lookup_order", {"visible": False, "reason": result.get("reason")})
                return {"final": {"status": "escalated", "error_reason": result.get("reason")}}
            memory["order"] = dict(result["order"])
            trace.add("lookup_order", safe_dump(result))
        elif last_tool == "lookup_refund_history":
            memory["history"] = {
                "refund_count": int(result.get("refund_count", 0)),
                "refunded_vnd": int(result.get("refunded_vnd", 0)),
            }
            trace.add("lookup_refund_history", safe_dump(memory["history"]))
        elif last_tool == "compute_compensation":
            memory["quote"] = safe_dump(result)
            trace.add("quote", memory["quote"])

        # Act: pick the next read tool, or finish.
        if "order_id" not in memory:
            return _tool("get_claim_view", claim_id=memory["claim_id"])
        if "order" not in memory:
            return _tool("lookup_order", order_id=memory["order_id"], principal_id=memory["principal_id"])
        if "history" not in memory:
            return _tool("lookup_refund_history", order_id=memory["order_id"], principal_id=memory["principal_id"])
        if "quote" not in memory:
            # Quote from the order row only. Ticket delay numbers are ignored.
            return _tool("compute_compensation", order=memory["order"])
        # Final: the agent proposes. Code re-reads the quote from memory after the loop.
        return {"final": {"status": "propose_refund"}}

    return decide


def _tool(name: str, **args: Any) -> dict[str, Any]:
    return {"tool": name, "args": args}


def _draft(budget: Budget, seed: int, status: str) -> None:
    """Reply text only. Not stored in the trace, not used for any decision."""
    complete(budget, seed=seed, purpose="draft", prompt=f"status={status}")
