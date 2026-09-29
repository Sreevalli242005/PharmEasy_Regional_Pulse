from queries import (
    get_connection,
    region_month_sales,
    build_sales_by_region_month
)

from metrics_engine import (
    compute_transition_changes,
    flag_significant_regions_v1
)


def build_metrics_bundle():
    """
    Gets the SQL-verified monthly sales data and calculates
    percentage changes for both monthly transitions.
    """

    conn = get_connection()

    try:
        rows = region_month_sales(conn)
    finally:
        conn.close()

    sales_by_region_month = build_sales_by_region_month(rows)

    apr_may_changes = compute_transition_changes(
        sales_by_region_month,
        "2026-04",
        "2026-05"
    )

    may_jun_changes = compute_transition_changes(
        sales_by_region_month,
        "2026-05",
        "2026-06"
    )

    return {
        "sales_by_region_month": sales_by_region_month,
        "apr_may_changes": apr_may_changes,
        "may_jun_changes": may_jun_changes,
        "apr_may_flagged": flag_significant_regions_v1(
            apr_may_changes,
            threshold=8
        ),
        "may_jun_flagged": flag_significant_regions_v1(
            may_jun_changes,
            threshold=8
        ),
    }


def _direction_word(pct):
    """Returns the direction of the percentage change."""

    if pct >= 0:
        return "up"

    return "down"


def _cii_block_for_region(region, metrics):
    """
    Builds one CII block for one flagged region.
    """

    sales = metrics["sales_by_region_month"][region]

    apr_may_pct = metrics["apr_may_changes"][region]
    may_jun_pct = metrics["may_jun_changes"][region]

    flagged_apr_may = region in metrics["apr_may_flagged"]
    flagged_may_jun = region in metrics["may_jun_flagged"]

    context_lines = []
    insight_lines = []

    # April -> May
    if flagged_apr_may:

        context_lines.append(
            f"April sales were INR {sales.get('2026-04', 0):,.2f}; "
            f"May sales were INR {sales.get('2026-05', 0):,.2f}."
        )

        insight_lines.append(
            f"{region} moved {_direction_word(apr_may_pct)} "
            f"{abs(apr_may_pct):.2f}% from April to May "
            f"(threshold: 8%)."
        )

    # May -> June
    if flagged_may_jun:

        context_lines.append(
            f"May sales were INR {sales.get('2026-05', 0):,.2f}; "
            f"June sales were INR {sales.get('2026-06', 0):,.2f}."
        )

        insight_lines.append(
            f"{region} moved {_direction_word(may_jun_pct)} "
            f"{abs(may_jun_pct):.2f}% from May to June "
            f"(threshold: 8%)."
        )

    # Create implication
    if flagged_apr_may and flagged_may_jun:

        if apr_may_pct > 8 and may_jun_pct > 8:

            implication = (
                f"{region} shows positive movement in both monthly "
                f"transitions. The next review should confirm whether "
                f"this increase is sustained."
            )

        elif apr_may_pct < -8 and may_jun_pct < -8:

            implication = (
                f"{region} shows negative movement in both monthly "
                f"transitions. The next review should confirm whether "
                f"this decline is sustained."
            )

        elif apr_may_pct > 8 and may_jun_pct < -8:

            implication = (
                f"{region} increased and then declined in the next month. "
                f"The next review should examine this change before any "
                f"resourcing decision."
            )

        else:

            implication = (
                f"{region} declined and then increased in the next month. "
                f"The next review should examine whether this rebound "
                f"is sustained."
            )

    else:

        implication = (
            f"{region} recorded a material monthly movement. "
            f"The next review should examine the underlying pattern "
            f"before any resourcing decision."
        )

    return {
        "region": region,
        "context": " ".join(context_lines),
        "insight": " ".join(insight_lines),
        "implication": implication,
    }


def draft_report_v1(flagged_regions, metrics):
    """
    Creates one CII block for each unique flagged region.
    """

    unique_regions = sorted(set(flagged_regions))

    return [
        _cii_block_for_region(region, metrics)
        for region in unique_regions
    ]


def print_report(blocks):
    """Prints the CII report."""

    for block in blocks:

        print(f"=== {block['region']} ===")
        print(f"Context:     {block['context']}")
        print(f"Insight:     {block['insight']}")
        print(f"Implication: {block['implication']}")
        print()


if __name__ == "__main__":

    metrics = build_metrics_bundle()

    union_flagged = (
        set(metrics["apr_may_flagged"])
        |
        set(metrics["may_jun_flagged"])
    )

    print(
        f"Union of flagged regions ({len(union_flagged)}): "
        f"{sorted(union_flagged)}\n"
    )

    report_blocks = draft_report_v1(
        union_flagged,
        metrics
    )

    print_report(report_blocks)