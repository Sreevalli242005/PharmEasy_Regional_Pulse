=> Recommendation Memo — Guntur April→May Sales Swing


=>Title

Guntur Region: +122.19% Sales Swing, April→May 2026 — Warrants Regional Lead Review [HIGH]


=>Context

PharmEasy Regional Pulse's Part 2 metrics engine computes month-on-month sales
change per region from SQL-verified totals in 'pharmeasy.db' [HIGH].
Across the 9 active regions, the significance-flagging rule ('flag_significant_regions_v1',threshold = 8%) flagged 7 of 9 regions in the April→May transition and 7 of 9 in the May→June transition [HIGH].
Guntur's April→May swing is the largest-magnitude flagged case across these transitions [HIGH].


=> Key Insight

Guntur's total sales rose from INR 62,442.27 in April to INR 138,738.93 in May
[HIGH], a month-on-month increase of +122.19% [HIGH].
This is more than 15 times the 8% operational-alert threshold [HIGH].
Guntur was also flagged in the May→June transition, with sales falling by 28.11% [HIGH].


=> Evidence

* 'region_month_sales()' calculates regional monthly sales using
  'SUM(sales_inr)' grouped by region and month [HIGH].
* April sales for Guntur: INR 62,442.27 [HIGH].
* May sales for Guntur: INR 138,738.93 [HIGH].
* June sales for Guntur: INR 99,745.18 [HIGH].
* Percentage change is calculated using
  '(current - previous) / previous * 100' [HIGH].
* Guntur moved +122.19% from April to May and -28.11% from May to June [HIGH].


=> Recommendation

Treat the May figure as a spike requiring confirmation rather than as a new
demand baseline for Guntur [MEDIUM]. 
Before reallocating inventory or staffing toward Guntur, a regional lead should confirm whether the observed change is supported by repeatable order and category patterns [MEDIUM].


=> Next Check

Re-run the pipeline when July data is available and check whether Guntur's
June→July movement supports or contradicts the observed May spike [MEDIUM].
The current dataset alone cannot establish whether the May increase represents
a sustained trend or a temporary movement [HIGH].


=> Assumptions

The analysis treats an 8% month-on-month change as the operational-alert
threshold defined for this analysis [HIGH]. 
The sales movement identifies an area for review but does not establish the underlying cause of the movement[HIGH].