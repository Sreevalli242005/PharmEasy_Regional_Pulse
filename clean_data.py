import pandas as pd

RAW_FILE = "pharmeasy_orders_raw.csv"
CLEAN_FILE = "orders_clean.csv"

REQUIRED_COLUMNS = [
    "order_id", "order_date", "region", "category", "product",
    "quantity", "sales_inr", "profit_inr",
]


CANONICAL_REGIONS = [
    "Hyderabad", "Warangal", "Vijayawada", "Visakhapatnam",
    "Guntur", "Nellore", "Tirupati", "Karimnagar", "Bengaluru",
]


def remove_exact_duplicates(df):
    before = len(df)
    deduped = df.drop_duplicates(keep="first")
    removed = before - len(deduped)
    return deduped, removed


def normalize_region(df):
    df = df.copy()
    df["region"] = df["region"].str.strip().str.title()
    return df


def build_product_category_lookup(df):
    known = df[df["category"].notna() & (df["category"] != "")]
    lookup = known.drop_duplicates("product").set_index("product")["category"].to_dict()
    return lookup


def impute_category(df):
    df = df.copy()
    lookup = build_product_category_lookup(df)
    missing_mask = df["category"].isna() | (df["category"] == "")
    df.loc[missing_mask, "category"] = df.loc[missing_mask, "product"].map(lookup)
    return df


def impute_profit(df):
    df = df.copy()
    df["profit_inr"] = pd.to_numeric(df["profit_inr"], errors="coerce")

    known = df[df["profit_inr"].notna()].copy()
    known["margin"] = known["profit_inr"] / known["sales_inr"]
    category_mean_margin = known.groupby("category")["margin"].mean()

    missing_mask = df["profit_inr"].isna()
    for idx in df[missing_mask].index:
        category = df.at[idx, "category"]
        margin = category_mean_margin[category]
        df.at[idx, "profit_inr"] = round(df.at[idx, "sales_inr"] * margin, 2)

    return df


def clean_pipeline(raw_df):
    stats = {}

    deduped, removed = remove_exact_duplicates(raw_df)
    stats["duplicates_removed"] = removed

    normalized = normalize_region(deduped)
    stats["distinct_regions_after_normalize"] = normalized["region"].nunique()

    stats["missing_category_before"] = int(
        (normalized["category"].isna() | (normalized["category"] == "")).sum()
    )
    with_category = impute_category(normalized)

    stats["missing_profit_before"] = int(
        pd.to_numeric(with_category["profit_inr"], errors="coerce").isna().sum()
    )
    with_profit = impute_profit(with_category)

    stats["rows_after_cleaning"] = len(with_profit)
    return with_profit, stats


def validate_schema(df, required_columns):
    missing = [col for col in required_columns if col not in df.columns]
    status = "blocked_schema" if missing else "validated"
    return {
        "status": status,
        "row_count": len(df),
        "missing_columns": missing,
    }


def main():
    raw_df = pd.read_csv(RAW_FILE, dtype={"category": "object", "profit_inr": "object"})

    clean_df, stats = clean_pipeline(raw_df)

    print("=== Cleaning summary ===")
    print(f"Raw rows loaded:            {len(raw_df)}")
    print(f"Exact duplicates removed:   {stats['duplicates_removed']}")
    print(f"Distinct regions (raw):     {raw_df['region'].nunique()}")
    print(f"Distinct regions (clean):   {stats['distinct_regions_after_normalize']}")
    print(f"Missing category imputed:   {stats['missing_category_before']}")
    print(f"Missing profit imputed:     {stats['missing_profit_before']}")
    print(f"Final clean row count:      {stats['rows_after_cleaning']}")

    remaining_missing_category = (clean_df["category"].isna() | (clean_df["category"] == "")).sum()
    remaining_missing_profit = clean_df["profit_inr"].isna().sum()
    print(f"Remaining missing category after imputation: {remaining_missing_category}")
    print(f"Remaining missing profit after imputation:   {remaining_missing_profit}")

    clean_df.to_csv(CLEAN_FILE, index=False)
    print(f"\nSaved cleaned dataset to {CLEAN_FILE}")

    print("\n=== Schema validation: clean data ===")
    result_ok = validate_schema(clean_df, REQUIRED_COLUMNS)
    print(result_ok)

    print("\n=== Schema validation: deliberately broken copy (drop 'profit_inr') ===")
    broken_df = clean_df.drop(columns=["profit_inr"])
    result_broken = validate_schema(broken_df, REQUIRED_COLUMNS)
    print(result_broken)


if __name__ == "__main__":
    main()