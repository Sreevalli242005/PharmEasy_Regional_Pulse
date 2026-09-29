import sqlite3

DB_FILE = "pharmeasy.db"


def get_connection():
    return sqlite3.connect(DB_FILE)


def row_count_check(conn):
    left_count = conn.execute("""
        SELECT COUNT(*)
        FROM regions_master r
        LEFT JOIN orders_clean o ON r.region = o.region
    """).fetchone()[0]

    inner_count = conn.execute("""
        SELECT COUNT(*)
        FROM regions_master r
        INNER JOIN orders_clean o ON r.region = o.region
    """).fetchone()[0]

    print("--- Task 2.2a: Row-count check (LEFT vs INNER JOIN) ---")
    print(f"LEFT JOIN row count:  {left_count}")
    print(f"INNER JOIN row count: {inner_count}")
    print(f"Delta (should be 1, Kurnool's null-padded row): {left_count - inner_count}")
    print()
    return left_count, inner_count


def duplicate_key_check(conn):
    rows = conn.execute("""
        SELECT order_id, COUNT(*) as cnt
        FROM orders_clean
        GROUP BY order_id
        HAVING COUNT(*) > 1
    """).fetchall()

    print("--- Task 2.2b: Duplicate-key check ---")
    print(f"Duplicate order_ids found: {len(rows)} (expected 0)")
    print()
    return rows


def null_vs_count_star_check(conn):
    rows = conn.execute("""
        SELECT
            r.region,
            COUNT(*) AS count_star,
            COUNT(o.order_id) AS count_order_id
        FROM regions_master r
        LEFT JOIN orders_clean o ON r.region = o.region
        GROUP BY r.region
        ORDER BY r.region
    """).fetchall()

    print("--- Task 2.2c: COUNT(*) vs COUNT(order_id) per region ---")
    print(f"{'region':<15} {'COUNT(*)':>10} {'COUNT(order_id)':>16} {'disagree?':>10}")
    disagreements = []
    for region, count_star, count_order_id in rows:
        disagree = count_star != count_order_id
        if disagree:
            disagreements.append(region)
        print(f"{region:<15} {count_star:>10} {count_order_id:>16} {str(disagree):>10}")
    print(f"\nRegions where COUNT(*) disagrees with COUNT(order_id): {disagreements}")
    print()
    return rows


def per_region_order_counts(conn):
    rows = conn.execute("""
        SELECT r.region, COUNT(o.order_id) AS order_count
        FROM regions_master r
        LEFT JOIN orders_clean o ON r.region = o.region
        GROUP BY r.region
        ORDER BY order_count ASC
    """).fetchall()

    print("--- Task 2.2d: Per-region order counts (ascending) ---")
    for region, order_count in rows:
        print(f"{region:<15} {order_count}")
    print()
    return rows

def region_month_sales(conn):
    rows = conn.execute("""
        SELECT
            region,
            substr(order_date, 1, 7) AS month,
            SUM(sales_inr) AS total_sales
        FROM orders_clean
        GROUP BY region, month
        ORDER BY region, month
    """).fetchall()

    print("--- Task 2.3: Total sales_inr per region per month ---")
    for region, month, total_sales in rows:
        print(f"{region:<15} {month}  {total_sales:>12,.2f}")
    print()
    return rows


def build_sales_by_region_month(rows):
    data = {}
    for region, month, total_sales in rows:
        data.setdefault(region, {})[month] = total_sales
    return data


if __name__ == "__main__":
    conn = get_connection()
    try:
        row_count_check(conn)
        duplicate_key_check(conn)
        null_vs_count_star_check(conn)
        per_region_order_counts(conn)
        region_month_sales(conn)
    finally:
        conn.close()