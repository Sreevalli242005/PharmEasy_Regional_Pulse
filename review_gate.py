import json
import uuid
from datetime import datetime, timezone

VALID_DECISIONS = {"approve", "edit", "reject"}
AUDIT_LOG_FILE = "audit_log.jsonl"


def review_gate_v1(report, decision, reviewer_note=""):
    if decision not in VALID_DECISIONS:
        raise ValueError(
            f"Invalid decision {decision!r}. Must be one of {sorted(VALID_DECISIONS)}."
        )

    downstream_allowed = decision == "approve"

    updated_report = dict(report)
    updated_report["decision"] = decision
    updated_report["reviewer_note"] = reviewer_note
    updated_report["downstream_use_allowed"] = downstream_allowed

    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "run_id": str(uuid.uuid4()),
        "region": report.get("region", "UNKNOWN"),
        "decision": decision,
        "reviewer_note": reviewer_note,
    }
    with open(AUDIT_LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return updated_report


def run_test_harness():
    test_cases = [
        {"report": {"region": "Guntur", "summary": "April-May +122.19% swing"}, "decision": "approve", "note": "Numbers verified against Part 2 SQL output."},
        {"report": {"region": "Hyderabad", "summary": "April-May +16.29% swing"}, "decision": "edit", "note": "Tighten the implication wording before sending."},
        {"report": {"region": "Visakhapatnam", "summary": "April-May -62.46% swing"}, "decision": "reject", "note": "Needs a second SQL pass before this goes anywhere."},
    ]

    for case in test_cases:
        before = dict(case["report"])
        after = review_gate_v1(case["report"], case["decision"], case["note"])
        print(f"--- Decision: {case['decision']} ---")
        print(f"Before: {before}")
        print(f"After:  {after}")
        print()

    print("--- Validation check: rejecting an invalid decision ---")
    try:
        review_gate_v1({"region": "Nellore"}, "maybe")
    except ValueError as e:
        print(f"Correctly rejected invalid decision: {e}")


if __name__ == "__main__":
    run_test_harness()