PharmEasy Regional Pulse

1. Project Overview

Monthly sales data is messy in pretty normal ways. Rows get duplicated, region names get typed differently by different people, some values go missing, and every so often a region's numbers move a lot more than usual.
Before anyone can trust a number enough to act on it, all of that needs to get sorted out first.

That's what this project does. It's one pipeline, start to finish. Raw order data goes in, gets cleaned, then the actual numbers get calculated through SQL so they can be checked, not just trusted. Any region that moved enough to matter gets flagged. The biggest one gets written up as a proper recommendation, but nothing gets used until a person actually approves it.
At the end, all of it shows up on a dashboard a regional manager can actually look at.


2. Key Finding

The one number worth paying attention to is what happened in Guntur
between April and May.

- April sales: ₹62,442.27
- May sales: ₹138,738.93
- April to May: up "122.19%"
- June sales: ₹99,745.18
- May to June: down "28.11%"
- The alert threshold used across the project is "8%" — any region that moves more than that, up or down, gets flagged so      someone can look at it

122% is a big number, obviously way past 8%, and it's the largest jump anywhere in the whole dataset. But then June dropped most of it back down, so I don't think it's fair to call May the new normal for Guntur. It looks more like a spike, and spikes need a second month before you can trust them.
I'll say plainly that I don't know why it happened. There's nothing in the data about promotions, stock changes, or anything else that could explain it, so I'm not going to guess and pass it off as fact.


3. What I Built

- 'generate_dataset.py' — the dataset generator, given as part of the assignment. I didn't change anything in it.

- 'clean_data.py' — takes out duplicate rows, fixes region spelling, fills in the gaps in category and profit, and checks the final result has all the columns it should.

- 'build_db.py' — puts the cleaned data into a database file, 'pharmeasy.db'.

- 'queries.py' — actual SQL, checking things like duplicate keys and how many orders each region has.

- 'metrics_engine.py' — works out the month-to-month change for each region, decides which ones get flagged, and can save/reload that data.

- 'draft_report.py' — turns the flagged regions into short write-ups (what happened, what it means, why it matters).

- 'memo.md' — a one-page memo about the Guntur numbers, with every claim marked by how sure I am about it.

- 'review_gate.py' and 'audit_log.jsonl' — nothing moves forward without someone approving, editing, or rejecting it first, and every one of those decisions gets written down.

- 'reliability_checklist.md' — the checks I went through before calling the memo done.

- 'app.py' — the dashboard.

- 'presentation_storyline.md' — the Guntur finding explained two different ways, depending on who's listening.


4. End-to-End Workflow

Raw Data → Cleaning → Validation → SQLite → SQL Analysis → Metrics Engine → CII → Memo → Review Gate → Audit Log →
Dashboard → Storyline

Here's roughly what happens at each stage. The raw data comes from 'generate_dataset.py'. Cleaning gets rid of duplicates, fixes region names, and fills in what's missing. Then there's a quick check to make sure nothing important got lost along the way. That cleaned data goes into a small SQLite database, and a handful of SQL checks confirm the database results are consistent with the expected relationships. From there, the metrics get calculated and any region that moved enough gets flagged. Flagged regions turn into short write-ups, and the biggest one becomes a full memo. That memo can't go anywhere until someone reviews it, and that review gets logged. Last comes the dashboard, which shows all of this, and the storyline, which explains
the same finding to two different kinds of people.


5. Data Quality and Reliability

- Started with 2,159 rows and 10 regions (9 with actual orders, plus Kurnool, which has none).

- 59 of those rows were exact duplicates. Removing them left 2,100 rows.

- The region column had 16 different spellings for what should only be 9 regions — things like " hyderabad", "HYDERABAD ", and "Hyderabad" all meaning the same place. Cleaning up the spacing and capitalization brought that down to exactly 9.

- 94 rows were missing a profit number. I filled those using the average profit margin for that product's category, not one flat number across everything, since margins are different between categories.

- 48 rows were missing a category. I built a simple lookup from product name to category using the rows that already had one, since each product only ever belongs to one category in this data anyway.

- I ran a schema check on the cleaned data and it passed. I also ran it on a copy with a column removed on purpose, and it correctly failed — so the check is actually doing something, not just always saying yes.

- On the database side, I checked that no order ID shows up twice, and it doesn't. I also compared two different ways of counting orders per region, and it catches something worth knowing: for Kurnool, which has zero real orders, one counting method wrongly says 1, while the correct method says 0. Kurnool stays visible the whole way through instead of quietly disappearing.

- I saved April's numbers, loaded them back separately, and checked they matched exactly.

- The review step only accepts approve, edit, or reject — anything else gets rejected — and every decision gets written to a log with a timestamp, the region, and a note.


6. Analysis Approach

Monthly sales per region come from grouping the data by region and month and adding up sales. The month-to-month change is just:

(Current Month - Previous Month) / Previous Month × 100

If the previous month was zero, the change is just set to zero instead of crashing the program. Anything whose change is more than 8% in either direction gets flagged. I want to be honest that this isn't some advanced statistical test — it's just a fixed cutoff, and with only a few hundred orders per region each month, going past 8% isn't actually unusual. Most
regions cross it most months. What makes Guntur different is how far past it the number is, which is why it's the one this whole project focuses on.

None of the flagged regions are typed in by hand anywhere. The code works it out fresh from the real data every time it runs. Across both months being compared, that adds up to 8 out of 9 active regions getting flagged at least once. Nellore is the one region that never gets flagged either time.


7. Four Key Outputs

The dashboard ('app.py') is the main one — run it with 'streamlit run app.py'. It opens with a short summary, then four number
cards up top (orders, sales, profit, active regions — and the order count is a real distinct count, not just a row count), a chart showing sales by month, a chart comparing regions, a breakdown by category, a table of
everything that got flagged, and a table you can filter down to one region. There's a short write-up on Guntur at the bottom.

'draft_report.py' is the CII report. Running it prints one short write-up per flagged region, 8 total, each in three parts — what happened, what it means, why it matters. A region flagged in both months gets one combined write-up instead of two.

'memo.md' is the one-page memo, focused just on Guntur. It uses the seven fields the assignment asked for, and every claim in it is marked as low, medium, or high risk depending on how directly it's backed by the actual numbers. I tried to be honest about which parts are solid and which parts are me reasoning it through.

'presentation_storyline.md' tells the same Guntur story twice — once the way you'd explain it to an executive, and once the way you'd explain it to a regional manager, since they care about different things. There are also
three questions in there that I think someone would actually push back with, answered as honestly as I could.


8. Repository Structure

PharmEasy-Regional-Pulse/
── generate_dataset.py
── clean_data.py
── data_quality_report.md
── build_db.py
── queries.py
── metrics_engine.py
── draft_report.py
── memo.md
── review_gate.py
── audit_log.jsonl
── reliability_checklist.md
── app.py
── presentation_storyline.md
── README.md
── requirements.txt


9. How to Run the Project

This is the exact order I ran everything in, from a clean folder, to make sure it actually works from scratch:

1. Create and activate a virtual environment:
python -m venv .venv
.venv\Scripts\activate        # Windows

2. Install dependencies:
pip install -r Requirements.txt

3. Generate the raw dataset:
python generate_dataset.py

4. Clean the data and run schema validation:
python clean_data.py

5. Build the SQLite database:
python build_db.py

6. Run SQL validation and region/month metrics:
python queries.py

7. Run the metrics engine:
python metrics_engine.py

8. Generate the CII report:
python draft_report.py

9. Run the review-gate test harness (writes audit_log.jsonl):
python review_gate.py

10. Launch the dashboard:
streamlit run app.py


10. Assumptions and Limitations

Things I'm confident about: the row counts and duplicate numbers, Guntur's three monthly totals and both percentage changes
(straight from the database, not typed in by hand), the list of 8 flagged regions, which gets worked out fresh every run instead of being fixed in the code, and the fact that the review step actually rejects anything that isn't approve, edit, or reject.

What I can't claim: why Guntur spiked in May. There's nothing in this dataset — no promotion field, campaign field, restocking field, or other external-event information — that can establish the cause. The memo therefore treats May as a spike that needs checking, not as proof of a sustained demand increase. I also can't say whether Guntur's numbers will do the same thing again — June's drop is the only extra data point I have, and that's not enough to call it a pattern either way.


11. Why This Approach

I cleaned the data before doing anything else because a percentage change worked out from duplicated rows or messy region names would be wrong in a way that's hard to notice later. Better to fix it once, at the start, and
write down what got fixed. I used SQL for the join and duplicate checks specifically because those are exactly the kind of mistake — a region with no orders quietly disappearing, a key getting counted twice — that's easy
to get wrong without noticing and easy to prove right or wrong once you write it as SQL. The flagging works out its list fresh every time instead of me just hard-coding "Guntur is the interesting one," so the same code
would still work correctly on a different month's data. There's a human review step before anything reaches a stakeholder because an 8% cutoff is just a noisy alert, not proof of anything on its own — it's meant to point
someone toward a number, not replace their judgment. And the dashboard isn't its own separate source of truth. Every number on it gets worked out from the database when it loads, not typed in separately somewhere else.


12. Final Evaluator Cover Note

Guntur's sales went up 122.19% from April to May, then dropped 28.11% the month after — so I'm treating that as a spike worth reviewing, not a confirmed trend.

Here are the four things to look at, and the order I'd suggest:

1. "Streamlit dashboard" ('app.py' — live data exploration).
 Run 'streamlit run app.py' and try the region filter yourself before reading anyone's take on it, mine included.

2. "CII narrative" 
   The summary at the top of the dashboard is written in that context-insight-implication format, as the dashboard itself is supposed to have. 'draft_report.py' has the longer version if you want more detail than the dashboard gives you.

3. "One-page memo" ('memo.md' — the recommendation).
 The actual advice: don't change anything about Guntur based on May alone, hold steady, and check again once July's numbers come in.

4. "Presentation storyline" (`presentation_storyline.md` — how you'ddefend it live).
 The same finding explained two different ways, plus the questions I'd expect someone to push back with.

The one assumption I'd flag upfront: the reason for Guntur's May increase is unknown from this dataset. The available data can show the movement, but it cannot establish what caused it.
