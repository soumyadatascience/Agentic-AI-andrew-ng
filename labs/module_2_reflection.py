"""A SQL reflection fixture: Python standard library, no LLM calls.
Run: python3 labs/module_2_reflection.py
"""
import sqlite3

V1 = """SELECT color, SUM(qty_delta * price) AS revenue
FROM events WHERE action = 'sale'
GROUP BY color ORDER BY revenue DESC LIMIT 1"""
V2 = V1.replace("SUM(qty_delta * price)", "SUM(-qty_delta * price)")


def run(rows):
    with sqlite3.connect(":memory:") as db:
        db.execute("CREATE TABLE events(color TEXT, action TEXT, qty_delta INT, price INT)")
        db.executemany("INSERT INTO events VALUES (?, ?, ?, ?)", rows)
        before = db.execute(V1).fetchone()
        # Fixed revised query demonstrates the correction; no model discovers it.
        after = db.execute(V2).fetchone()
    return {"v1": before, "feedback": "Sales reduce inventory; negate sale quantities.",
            "v2": after}


def verify():
    cases = [
        ([("blue", "sale", -3, 20), ("red", "sale", -1, 20),
          ("red", "restock", 10, 20)], ("blue", 60)),
        ([("blue", "sale", -1, 10), ("red", "sale", -4, 10),
          ("blue", "return", 6, 10)], ("red", 40)),
    ]
    scores = {"v1": 0, "v2": 0}
    for rows, expected in cases:
        result = run(rows)
        for version in scores:
            scores[version] += result[version] == expected
        assert result["v2"] == expected
    print(f"V1: {scores['v1']}/2 correct; V2: {scores['v2']}/2 correct")
    print("PASS: sale-only gross revenue excludes returns and restocking")


if __name__ == "__main__":
    verify()
    result = run([("blue", "sale", -3, 20), ("red", "sale", -1, 20),
                  ("red", "restock", 10, 20)])
    print("V1:", result["v1"])
    print("V2:", result["v2"])
