"""Engineering extension: a bounded purchase command with atomic in-memory commit.
Not a sandbox, durable database transaction, or live model. Single-process fixture.
Run: python3 labs/module_5_planning.py
"""
from copy import deepcopy


def seed():
    return {"stock": {"Classic": 10, "Aviator": 23}, "balance": 500,
            "transactions": [], "receipts": {}}


PRICES = {"Classic": 60, "Aviator": 80}


def purchase(state, request_id, lines, fail_after=None):
    if not isinstance(request_id, str) or not request_id:
        return {"status": "invalid_request"}
    if not isinstance(lines, list) or not lines:
        return {"status": "invalid_request"}
    quantities = {}
    for line in lines:
        if not isinstance(line, dict) or set(line) != {"product", "qty"}:
            return {"status": "invalid_request"}
        name, qty = line["product"], line["qty"]
        if not isinstance(name, str) or name not in PRICES or type(qty) is not int or qty <= 0:
            return {"status": "invalid_request"}
        quantities[name] = quantities.get(name, 0) + qty
    fingerprint = tuple(sorted(quantities.items()))
    if request_id in state["receipts"]:
        prior = state["receipts"][request_id]
        return {"status": "already_applied" if prior == fingerprint else "id_conflict"}
    if any(qty > state["stock"][name] for name, qty in quantities.items()):
        return {"status": "insufficient_stock"}
    candidate = deepcopy(state)
    for index, (name, qty) in enumerate(quantities.items(), 1):
        candidate["stock"][name] -= qty
        candidate["balance"] += PRICES[name] * qty
        candidate["transactions"].append({"product": name, "qty": qty,
                                           "balance": candidate["balance"]})
        if index == fail_after:
            return {"status": "execution_failed"}  # Original state unchanged.
    candidate["receipts"][request_id] = fingerprint
    state.update(candidate)  # One commit in this single-threaded fixture.
    return {"status": "success"}


def verify():
    state = seed()
    lines = [{"product": "Classic", "qty": 3}, {"product": "Aviator", "qty": 1}]
    before = deepcopy(state)
    assert purchase(state, "r1", lines, fail_after=1)["status"] == "execution_failed"
    assert state == before
    assert purchase(state, "r1", lines)["status"] == "success"
    assert state["stock"] == {"Classic": 7, "Aviator": 22}
    assert [r["balance"] for r in state["transactions"]] == [680, 760]
    after = deepcopy(state)
    assert purchase(state, "r1", lines)["status"] == "already_applied"
    assert state == after
    assert purchase(state, "r1", [{"product": "Classic", "qty": 1}])["status"] == "id_conflict"
    assert purchase(state, "r2", [{"product": "Classic", "qty": 99}])["status"] == "insufficient_stock"
    assert purchase(state, "r3", [{"product": "Classic", "qty": -1}])["status"] == "invalid_request"
    assert purchase(state, "r4", [{"product": "Classic", "qty": 4}, {"product": "Classic", "qty": 4}])["status"] == "insufficient_stock"
    assert state == after
    print("Classic: 10 -> 7; Aviator: 23 -> 22; balance: 500 -> 760")
    print("Retry: already_applied; injected failure: no partial write")
    print("PASS: validation, totals, staged commit, retries, conflicting IDs")


if __name__ == "__main__":
    verify()
