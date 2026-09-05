"""Module 1 teaching lab. Python standard library only; no API calls or email sends.

Run: python3 workflow.py
Model steps, order lookup, and human decisions use explicit test fixtures.
"""
from copy import deepcopy
import json


REQUEST = {
    "order_id": "8847",
    "expected": "blue blender",
    "received": "red toaster",
    "deadline": "this weekend",
}
ORDERS = {"8847": {"product": "blue blender", "status": "delivered"}}


def run_workflow(approved=False, order_id="8847"):
    trace, outbox = [], []

    def step(name, value, function):
        before = deepcopy(value)
        outbox_before = deepcopy(outbox)
        try:
            result = function(value)
        except Exception as error:
            trace.append({"step": name, "input": before,
                          "error": str(error), "outbox_before": outbox_before,
                          "outbox_after": deepcopy(outbox)})
            raise
        trace.append({"step": name, "input": before,
                      "output": deepcopy(result), "outbox_before": outbox_before,
                      "outbox_after": deepcopy(outbox)})
        return result

    # This fixture stands in for extraction by a model.
    request = step("extract", {"order_id": order_id},
                   lambda value: {**REQUEST, **value})
    order = step("lookup", request,
                 lambda value: deepcopy(ORDERS.get(value["order_id"])))
    if order is None:
        return {"status": "order_not_found", "trace": trace, "outbox": outbox}

    # This deterministic draft stands in for generation by a model.
    draft = step("draft", {"request": request, "order": order},
                 lambda value: (
                     f"I'm sorry you received a {value['request']['received']} "
                     f"instead of your {value['order']['product']}. "
                     "I understand you need it this weekend. "
                     "Our team will review the delivery issue."
                 ))
    decision = step("review", draft, lambda value: {"approved": approved})
    if not decision["approved"]:
        return {"status": "review_rejected", "trace": trace, "outbox": outbox}

    def simulate_send(value):
        outbox.append(value)
        return {"receipt": "SIMULATED-001"}

    step("send", draft, simulate_send)
    return {"status": "sent_simulated", "trace": trace, "outbox": outbox}


def verify():
    rejected = run_workflow(approved=False)
    assert rejected["status"] == "review_rejected"
    assert rejected["outbox"] == []
    assert [s["step"] for s in rejected["trace"]] == ["extract", "lookup", "draft", "review"]
    accepted = run_workflow(approved=True)
    assert accepted["status"] == "sent_simulated"
    assert len(accepted["outbox"]) == 1
    assert accepted["trace"][-1]["outbox_before"] == []
    assert accepted["trace"][-1]["outbox_after"] == accepted["outbox"]
    assert accepted["trace"][1]["input"]["order_id"] == "8847"
    missing = run_workflow(approved=True, order_id="missing")
    assert missing["status"] == "order_not_found"
    assert missing["outbox"] == []
    print("PASS: approval, rejection, missing order, and trace snapshots")


if __name__ == "__main__":
    verify()
    for approved in (False, True):
        result = run_workflow(approved=approved)
        print(f"approved={approved} -> {result['status']}; outbox={len(result['outbox'])}")
    print("\nApproved run trace:")
    print(json.dumps(run_workflow(approved=True)["trace"], indent=2))
