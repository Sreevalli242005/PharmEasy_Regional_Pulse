import sqlite3
import pandas as pd

CLEAN_ORDERS_FILE = "orders_clean.csv"
REGIONS_FILE = "regions_master.csv"
DB_FILE = "pharmeasy.db"


def build_database():
    orders_df = pd.read_csv(CLEAN_ORDERS_FILE)
    regions_df = pd.read_csv(REGIONS_FILE)

    conn = sqlite3.connect(DB_FILE)
    try:
        regions_df.to_sql("regions_master", conn, if_exists="replace", index=False)
        orders_df.to_sql("orders_clean", conn, if_exists="replace", index=False)
        conn.commit()

        cur = conn.cursor()
        regions_count = cur.execute("SELECT COUNT(*) FROM regions_master").fetchone()[0]
        orders_count = cur.execute("SELECT COUNT(*) FROM orders_clean").fetchone()[0]

        print(f"Built {DB_FILE}")
        print(f"  regions_master: {regions_count} rows")
        print(f"  orders_clean:   {orders_count} rows")
    finally:
        conn.close()


if __name__ == "__main__":
    build_database()