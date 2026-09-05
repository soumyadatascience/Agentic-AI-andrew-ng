"""Provider-neutral fixture protocol, not a vendor API response format.
Run: python3 labs/module_3_tools.py. No network calls or real effects.
"""
import json


def get_time(timezone):
    return {"timezone": timezone, "time": "08:00", "fixture": True}


REGISTRY = {"get_time": get_time}


def dispatch(call):
    try:
        if call["name"] not in REGISTRY:
            raise ValueError("unknown tool")
        args = json.loads(call["arguments"])
        if not isinstance(args, dict) or set(args) != {"timezone"}:
            raise ValueError("expected only timezone")
        if args["timezone"] not in ("UTC", "Pacific/Auckland"):
            raise ValueError("unsupported fixture timezone")
        return {"ok": True, "value": REGISTRY[call["name"]](**args)}
    except (KeyError, ValueError, TypeError, RuntimeError) as error:
        return {"ok": False, "error": str(error)}


def run(model, max_turns=3):
    messages = [{"role": "user", "content": "What time is it?"}]
    for _ in range(max_turns):
        response = model(messages)
        messages.append(response)  # Once per response, even with two calls.
        calls = response.get("tool_calls", [])
        if calls:
            ids = [call["id"] for call in calls]
            if len(ids) != len(set(ids)):
                return {"status": "invalid_call_ids", "messages": messages}
            for call in calls:
                messages.append({"role": "tool", "tool_call_id": call["id"],
                                 "content": json.dumps(dispatch(call))})
        else:
            return {"status": "complete", "answer": response.get("content", ""),
                    "messages": messages}
    return {"status": "turn_limit", "messages": messages}


def call(call_id, arguments='{"timezone":"UTC"}', name="get_time"):
    return {"id": call_id, "name": name, "arguments": arguments}


def verify():
    responses = iter([
        {"role": "assistant", "content": "Let me check both.",
         "tool_calls": [call("a"), call("b", '{"timezone":"Pacific/Auckland"}')]},
        {"role": "assistant", "content": "Both fixture clocks return 08:00."},
    ])
    result = run(lambda _: next(responses))
    assert [m["role"] for m in result["messages"]] == ["user", "assistant", "tool", "tool", "assistant"]
    assert [m["tool_call_id"] for m in result["messages"] if m["role"] == "tool"] == ["a", "b"]
    assert run(lambda _: {"role": "assistant", "content": "Hello"})["status"] == "complete"
    assert not dispatch(call("c", "broken JSON"))["ok"]
    assert not dispatch(call("c", '{"timezone":3}'))["ok"]
    assert not dispatch(call("c", name="delete_email"))["ok"]
    def failing_tool(**kwargs):
        raise RuntimeError("fixture service failure")
    original = REGISTRY["get_time"]
    try:
        REGISTRY["get_time"] = failing_tool
        assert not dispatch(call("c"))["ok"]
    finally:
        REGISTRY["get_time"] = original
    repeated = lambda _: {"role": "assistant", "tool_calls": [call("repeat")]}
    assert run(repeated, max_turns=2)["status"] == "turn_limit"
    print("PASS: no tool, two calls, correlation, validation, tool error, turn limit")
    print("History: user -> assistant -> tool -> tool -> assistant")


if __name__ == "__main__":
    verify()
