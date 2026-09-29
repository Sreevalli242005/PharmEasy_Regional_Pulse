Data Quality Report — PharmEasy Regional Pulse

Before trusting any number that comes out of this pipeline, the raw data needed to be checked and cleaned first. This report goes through what was actually wrong with 'pharmeasy_orders_raw.csv' (2,159 rows) and what 'clean_data.py' did about it to produce 'orders_clean.csv' (2,100 rows). Each of the 7 standard data-quality dimensions is covered below.


1. Uniqueness

The raw file had 59 exact-duplicate rows — all 8 columns identical, probably from copy-pasting the same order in from more than one source sheet during the export. 'remove_exact_duplicates()' just drops anything that matches another row completely, which took the count from 2,159 down to 2,100. Easy to check: the row count before and after tells you it worked.


2. Consistency

Same region, sixteen different ways of writing it. The raw 'region' column had 16 distinct strings for what should only be 9 regions — "Hyderabad", " hyderabad", and "HYDERABAD " are all the same place, just typed differently by whoever was entering the data. normalize_region() strips the extra whitespace and title-cases everything, which collapses all 16 variants down to exactly the 9 names that match 'regions_master.csv'. Checking 'df["region"].nunique()' after normalization confirms it — 9, not 16.


3. Completeness

After removing duplicates, 48 rows had no 'category' and 94 had no 'profit_inr' — gaps that presumably didn't make it through whatever sync process feeds this export. Two different fixes for two different gaps: 'impute_category()' builds a lookup from product name to category using the rows that already had one (every product only ever belongs to one category here, so this isn't a guess), and 'impute_profit()' fills in the missing profit using that category's average margin applied to the row's
own sales figure. After both run, zero missing values remain in either column.


4. Validity

Before imputation, the missing 'profit_inr' values were empty strings, not actual numbers — which would break any SUM or AVG the moment it hit real math. 'clean_data.py' coerces the column to numeric with 'pd.to_numeric' before doing anything else with it, so by the time imputation runs, every value is a proper float. 'validate_schema()' confirms the final result has every required column, correctly typed, before it's allowed anywhere near Part 2's database.


5. Accuracy

This one's about not overcorrecting. Filling every missing profit value with one flat number — say, the dataset-wide average — would've been technically "complete" but actually wrong, since profit margins are pretty different across the 6 categories (Lab Tests and Medical Devices don't make the same margin as OTC Medicines). So the fix works at the category level instead of globally: each missing value gets that specific category's average margin, which keeps the imputed number closer to
reality than a one-size-fits-all fill would.


6. Timeliness

The dataset covers three months back to back — April, May, June 2026. If cleaning had accidentally dropped rows from any one of those months, the month-on-month comparisons in Part 2 would be comparing a full month against a partial one, which would make the percentage changes meaningless. Nothing in 'clean_data.py' filters by date, so all three months stay intact — checking 'order_date' in the cleaned file confirms it still spans April through June with nothing missing.


7. Relevance

Kurnool has zero orders on purpose — it's the dataset's built-in zero-activity region, needed later for Part 2's join logic. The risk was that a careless cleaning script might filter 'regions_master.csv' down to "only regions that appear in the orders," which would quietly delete Kurnool and break that test case. 'clean_data.py' never touches 'regions_master.csv' at all — cleaning only happens to the order rows — so Kurnool stays in the master list, all 10 regions accounted for, right
through to the end.




=>Summary table

----------------------------------------------------------------------------------------------------------
|               |                                                |                                        |
|  Dimension    |             Problem in raw data                |        Fix in 'clean_data.py'          |
|---------------|------------------------------------------------|----------------------------------------|
| Uniqueness    | 59 exact-duplicate rows                        | 'remove_exact_duplicates()'            |
|---------------|------------------------------------------------|----------------------------------------|
| Consistency   | 16 region string variants for 9 regions        | 'normalize_region()'                   |
|---------------|------------------------------------------------|----------------------------------------|
| Completeness  | 48 missing category, 94 missing profit         | 'impute_category()`, `impute_profit()' |
|---------------|------------------------------------------------|----------------------------------------|
| Validity      | 'profit_inr' non-numeric on missing rows       | 'pd.to_numeric' + imputation           |
|---------------|------------------------------------------------|----------------------------------------|
| Accuracy      | Global fill would distort category margins     | Per-category mean margin               |
|---------------|------------------------------------------------|----------------------------------------|
| Timeliness    | Three-month window must stay intact            | No date-based row dropping             |
|---------------|------------------------------------------------|----------------------------------------|
| Relevance     | Kurnool (zero-order region) must be preserved  | Master list untouched by cleaning      |
-----------------------------------------------------------------------------------------------------------