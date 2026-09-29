=>Reliability Checklist — memo.md (Guntur April→May Finding)

1. Safety check
No personally identifiable customer data appears in 'memo.md' or
'draft_report.py' CII blocks — every figure quoted is a region-level
aggregate ('SUM(sales_inr)' per region per month), never an individual
'order_id', customer name, or contact detail.

2. Validation
Every numeric claim in 'memo.md' (April total INR 62,442.27, May total
INR 138,738.93, +122.19% change, May→June -28.11%) was cross-checked against
the printed output of 'queries.py' and 'metrics_engine.py' run against
'pharmeasy.db', not retyped from memory or estimated.

3. Critique/refine
The first draft of the memo's Recommendation field stated the May spike as a
"new demand baseline" for Guntur; this was revised after noting the
May→June transition shows sales falling back toward the April level, so the
memo now explicitly frames May as an unconfirmed spike, not a trend.

4. Human sign-off
'memo.md' was passed through 'review_gate_v1()' with 'decision="approve"'
and reviewer note "Numbers verified against Part 2 SQL output," logged as
the first entry in 'audit_log.jsonl' before being treated as ready for the
dashboard/presentation stage.