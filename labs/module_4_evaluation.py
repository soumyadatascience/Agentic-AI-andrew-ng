"""An evaluation ledger with overlapping failure labels; no model calls.
Run: python3 labs/module_4_evaluation.py
"""
from collections import Counter
from urllib.parse import urlsplit


def preferred_ratio(urls, domains):
    if not urls:
        return 0.0
    # Exact host comparison, not substring matching in a URL.
    return sum(urlsplit(url).hostname in domains for url in urls) / len(urls)


def evaluate(cases, outputs):
    if not cases:
        raise ValueError("evaluation requires cases")
    runs = [{"id": case["id"], "expected": case["expected"],
             "actual": outputs[case["id"]],
             "pass": outputs[case["id"]] == case["expected"]} for case in cases]
    return {"accuracy": sum(r["pass"] for r in runs) / len(runs), "runs": runs}


def label_rates(failed_ledger):
    counts = Counter(label for row in failed_ledger for label in set(row["labels"]))
    n = len(failed_ledger)
    return {label: count / n for label, count in counts.items()} if n else {}


def verify():
    cases = [{"id": str(i), "expected": "2026-09-30"} for i in range(4)]
    baseline = {"0": "2026-09-30", "1": "2026-09-01", "2": "unknown", "3": "2026-09-01"}
    revised = {**baseline, "1": "2026-09-30", "3": "2026-09-30"}
    before, after = evaluate(cases, baseline), evaluate(cases, revised)
    assert before["accuracy"] == .25 and after["accuracy"] == .75
    ledger = [{"id": "1", "labels": ["date_selection"]},
              {"id": "2", "labels": ["pdf_to_text", "date_selection"]},
              {"id": "3", "labels": ["date_selection"]}]
    rates = label_rates(ledger)
    assert rates["date_selection"] == 1 and rates["pdf_to_text"] == 1/3
    assert preferred_ratio([], {"example.org"}) == 0
    assert preferred_ratio(["https://example.org/a", "https://example.org.evil.test/a"], {"example.org"}) == .5
    try:
        evaluate([], {})
    except ValueError:
        pass
    else:
        raise AssertionError("empty evaluation should be explicit")
    print("Accuracy: 25% -> 75% on 4 fixture cases")
    print("Failed-case labels: date_selection 3/3; pdf_to_text 1/3")
    print("PASS: paired cases, overlapping labels, empty inputs, exact hostname")


if __name__ == "__main__":
    verify()
