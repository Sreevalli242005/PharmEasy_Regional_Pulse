Presentation Storyline — Guntur April → May +122.19% Finding


1. For an Executive (Situation–Complication–Resolution)

Situation:
Between April and June 2026, PharmEasy's 9 active regions brought in ₹3,265,191.42 across 2,100 distinct orders. Every region gets checked monthly against an 8% month-on-month move threshold, and that caught 7 of the 9 regions in April → May, and 7 of 9 again in May → June.

Complication:
Guntur is the one that stands out. Sales went from ₹62,442.27 in April to ₹138,738.93 in May — a jump of +122.19%, more than 15 times past the alert threshold and the biggest single move anywhere in the data. Then in June it dropped back to ₹99,745.18, 
a -28.11% fall. So May sits between two lower months rather than looking like a new normal.

Resolution: 
Don't shift inventory or staff toward Guntur based on one month. Hold the current plan, run the pipeline again once July's numbers come in, and only treat this as an actual trend if June→July keeps moving the same direction. That way the decision stays reversible until there's one more month of evidence.



2. For a Regional Manager (Overview–Category–Detail)

Overview: 
Guntur's sales jumped 122.19% from April to May — the biggest month-on-month move out of all 9 regions this quarter.

Category: 
Here's the honest gap: the data doesn't show which category drove this. The swing shows up in Guntur's total sales for the month, but nothing in the dataset breaks that down by which of the 6 categories contributed more or less. That's worth saying out loud rather than guessing at an answer.

Detail:
These numbers come from 'region_month_sales()' in 'queries.py' — a straightforward 'SUM(sales_inr) GROUP BY region,month'
against the 2,100-row 'orders_clean' table — and the percentage change is calculated by 'compute_percentage_change_v1()'
in 'metrics_engine.py'. The May → June drop of -28.11% for the same region was worked out the exact same way,
which is why this is being treated as a spike to check on, not a newbaseline to plan around.


=>Anticipated Stakeholder Pushback

1. "Why should I believe this number?"

Fair question — a +122.19% swing is a big enough number that it deserves some carefull review before anyone acts on it. What's actually solid here: both the April (₹62,442.27) and May (₹138,738.93) totals come straight out of SQL, run against the cleaned, deduplicated 2,100-row table, and the percentage-change formula itself is nothing unusual. What's not settled is whether May reflects real, lasting demand or just a short-term spike — especially since the same region dropped -28.11% the very next month. The way to actually resolve this is to re-run the same pipeline once July's data is in. That one extra month will show whether the trend keeps going, reverses further, or settles back down.


2. "What if an alternative explanation is driving this?"

Also fair — a jump this size in a single month could easily come from something other than organic growth. A promotion, a restocking push, even a data quirk are all plausible. What's verified: the order-level data itself for Guntur in May — order counts, sales, categories — all traceable back to specific rows in 'orders_clean'. What's not verified: any actual
cause, because this dataset simply doesn't have fields for promotions, campaigns, or other business events. 'memo.md' says this directly — it's flagged as an open assumption, not treated as settled. The fastest way to close this gap would be checking with whoever runs operations in Guntur about anything that happened in May — that's a same-day conversation, not
a long investigation, and it should happen before any resourcing call gets made.


3. "What did you not check?"

Also a fair thing to ask. The pipeline is thorough about validating its own numbers, but it doesn't — and can't — verify everything about the business context behind them. What's actually checked: schema validation, duplicate removal, the join logic that proves Kurnool's zero-order status is handled correctly, and every percentage-change calculation. 
What's not checked: which category within Guntur drove the May number (the data doesn't support breaking it down that far), and whatever actually caused the spike in the first place. Both gaps are written down already, in 'reliability_checklist.md' validation step and in 'memo.md' Assumptions field, and both would get closed the same way — the July re-run, plus an actual conversation with someone on the ground in Guntur, ideally before the next monthly review.