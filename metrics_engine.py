import json

from queries import get_connection, region_month_sales, build_sales_by_region_month

STATE_DIR = "state"


def compute_percentage_change_v1(current, previous):
    if previous == 0:
        return 0
    return (current - previous) / previous * 100


def flag_significant_regions_v1(changes, threshold=8):
    return [region for region, pct in changes.items() if abs(pct) > threshold]


def save_state_v1(month_summary, path):
    with open(path, "w") as f:
        json.dump(month_summary, f, indent=2)


def load_previous_state_v1(path):
    with open(path) as f:
        return json.load(f)


def compute_transition_changes(sales_by_region_month, month_a, month_b):
    changes = {}
    for region, months in sales_by_region_month.items():
        previous = months.get(month_a, 0)
        current = months.get(month_b, 0)
        changes[region] = compute_percentage_change_v1(current, previous)
    return changes


def main():
    import os
    os.makedirs(STATE_DIR, exist_ok=True)

    conn = get_connection()
    try:
        rows = region_month_sales(conn)
    finally:
        conn.close()

    sales_by_region_month = build_sales_by_region_month(rows)

    april_summary = {region: months.get("2026-04", 0) for region, months in sales_by_region_month.items()}
    save_state_v1(april_summary, f"{STATE_DIR}/2026-04_summary.json")
    reloaded_april = load_previous_state_v1(f"{STATE_DIR}/2026-04_summary.json")
    print("--- State persistence round-trip check ---")
    print(f"Saved April summary == reloaded April summary: {april_summary == reloaded_april}")
    print()

    may_summary = {region: months.get("2026-05", 0) for region, months in sales_by_region_month.items()}
    save_state_v1(may_summary, f"{STATE_DIR}/2026-05_summary.json")

    june_summary = {region: months.get("2026-06", 0) for region, months in sales_by_region_month.items()}
    save_state_v1(june_summary, f"{STATE_DIR}/2026-06_summary.json")

    # April -> May
    apr_may_changes = compute_transition_changes(sales_by_region_month, "2026-04", "2026-05")
    apr_may_flagged = flag_significant_regions_v1(apr_may_changes, threshold=8)

    print("--- April -> May: percentage change per region ---")
    for region, pct in sorted(apr_may_changes.items()):
        print(f"{region:<15} {pct:>8.2f}%")
    print(f"\nFlagged (|change| > 8): {sorted(apr_may_flagged)}")
    print()

    # May -> June
    may_jun_changes = compute_transition_changes(sales_by_region_month, "2026-05", "2026-06")
    may_jun_flagged = flag_significant_regions_v1(may_jun_changes, threshold=8)

    print("--- May -> June: percentage change per region ---")
    for region, pct in sorted(may_jun_changes.items()):
        print(f"{region:<15} {pct:>8.2f}%")
    print(f"\nFlagged (|change| > 8): {sorted(may_jun_flagged)}")
    print()

    union_flagged = sorted(set(apr_may_flagged) | set(may_jun_flagged))
    print(f"--- Union of flagged regions across both transitions ---")
    print(f"{union_flagged}  (count: {len(union_flagged)})")

    return {
        "apr_may_changes": apr_may_changes,
        "apr_may_flagged": apr_may_flagged,
        "may_jun_changes": may_jun_changes,
        "may_jun_flagged": may_jun_flagged,
        "union_flagged": union_flagged,
    }


if __name__ == "__main__":
    main()