# Insights: what their numbers are telling them

People give us their data every day (SMS, statements, the Profile). This mode gives something back. It goes beyond the totals and says **what the numbers mean** and **what one move would change**.

Use it:
- when they ask "where is my money going?", "how am I doing?" or "what can I change?"
- in every **weekly check-in** and **scheduled run** (Part 3 of `sms-inbox.md`)
- at **month end**, after the Month-End Check (`coaching-modes.md` §3)
- when they ask for a **dashboard**

## 1. Get the facts (do the maths in code)

| Planner is… | Do this |
|---|---|
| A file you can open (.xlsx) | `python3 scripts/fnsoko_tools.py insights --planner PLANNER.xlsx [--month 2026-11] [--whatif "Eating out:2000"] [--today 2026-11-12]` (`--today` defaults to today; set it in scheduled runs so the week and pace are for the run's date) |
| In Google Sheets (connector) | Read the ranges below, build `data.json` in the shape below, then run `insights --data data.json`. If you can't run code, follow the same steps by hand and label the results ESTIMATED |
| Not available | Ask them to paste this month's Money Log rows and their budget. Work from that only |

**Ranges to read in Google Sheets** (v6; v5 differences in brackets):
- Setup `B13:F27` (categories by group: B Income, C Bills, D Everyday, E Savings, F Debt) and `B36:E50` (Need/Want tags)
- Money Log `B10:E2009` (date, category, amount, note)
- My Budget `B10:O100` (B name, C usual, D..O = Jan..Dec, so D = Jan and N = Nov). Drop the section headings, the Category header rows and the Total rows. Short rows from the connector just mean empty months
- My Money Profile `B23:E37` income and `B43:D72` must-pay with due day in D (v5: `B23:E28`, `B34:D43`)
- Workings `C214` essentials, `C215` fund target, `C218` fund balance, `C196` ladder step, `B252:H263` goals (B name, D date, G target, H saved; include only goals with a target)
- My Loans `C17:I24` (C name, F owe, G rate, H per year/month, I minimum payment) and `H9:H11` (plan start, extra a month, method)
- Month-End Check `E16:P23` (balances, Jan..Dec) and `I31:I42` (not logged, Jan..Dec); My Emergency Fund `H8` (months) and `H11` (fund category); My Money Ladder `G30`
- For the extra dashboard tabs: Workings `C222:C226` (fund pace), `B251:M263` (goal status: L per month, K months left, M status), `C296:C304` and `O287:O294` (debt plan), `D134:O137` (net worth own / owe / net / month typed) with `B150:C159` (own by type), `C147:C148`; My Future `C6:C13`

**`data.json` shape** (leave out what you don't have; the script skips that part):

```json
{"currency": "KSh",
 "categories": {"Income": [], "Bills": [], "Everyday": [], "Savings": [], "Debt": []},
 "needs": {"Rent": "Need", "Eating out": "Want"},
 "fees_category": "Bank & M-Pesa fees",
 "log": [{"date": "2026-11-03", "category": "Groceries", "amount": 2300, "note": "Supermarket"}],
 "budget": {"Groceries": {"usual": 12000, "months": {"12": 15000}}},
 "bills_due": [{"name": "Rent", "amount": 18000, "day": 5}],
 "emergency_fund": {"essentials": 40000, "target": 120000, "balance": 15000, "category": "Emergency fund"},
 "goals": [{"name": "Laptop", "target": 80000, "saved": 10000, "date": "2027-06-30"}],
 "loans": [{"name": "Mobile loans", "owe": 5000, "rate": 0.075, "per": "month", "payment": 1500}],
 "month_end_balances": {"10": 7000}, "not_logged": {"10": 2500},
 "ladder_step": 2, "expensive_from": 0.2,
 "loan_plan": {"start": "Nov 2026", "extra": 0, "method": "Avalanche: highest interest first", "debt_free_by": "Feb 2027", "months": 4,
               "interest_plan": 968, "debt_free_by_min": "Feb 2027", "interest_min": 968, "interest_saved": 0, "months_sooner": 0,
               "pay_this_month": [{"name": "Mobile loans", "pay": 1500}]},
 "goal_status": [{"name": "Laptop", "horizon": "Short-term", "per_month": 8000, "months_left": 8, "status": "On track"}],
 "fund_plan": {"months_target": 6, "months_to_target": 5, "target_date": "Apr 2027", "avg_per_month": 3000},
 "net_worth": {"own": [12 values Jan..Dec], "owe": [12], "net": [12], "typed": [12], "by_type": [["Cash & M-Pesa", 7000]],
               "change_since_first": 19000, "first_month_name": "August"},
 "future": {"age": 30, "stop_age": 60, "income_wanted": 60000, "saved": 0, "monthly": 9250, "return": "10%", "inflation": "5%", "spend_rate": "4%"}}
```

Google Sheets returns formatted text (`"40,699"`, `"7.5%"`, `"1 Aug 2026"`, `"per month"`). Put it in as it comes; the script reads all of these.

The output is JSON facts. **You write the words.** Never show the JSON.

## 2. The insights, and how to say them

Always start with **coverage**: "Based on what's logged (about 96% of October)", or "ESTIMATED: no month-end balances yet." A leak in a half-logged month may just be a gap in the log.

| Insight (output key) | What it shows | Say it like |
|---|---|---|
| **Fees** (`leaks.fees`) | Total M-Pesa and bank fees, and their share of spending | "KSh 1,840 went on fees this month. That's about a week of groceries." Then one tip, such as fewer and bigger transfers instead of many small ones, or paying from the wallet that charges less. Point them to Safaricom's or their bank's current tariff; don't quote charges from memory |
| **Borrowing cost** (`leaks.borrowing`, `leaks.loan_costs`) | How often they borrowed; each loan's monthly rate as a yearly rate | "Fuliza at 7.5% a month is about 90% a year (138% when it compounds)." Use the planner's rates; for Fuliza, ask them to check the current daily fee in the app. Expensive = at or above My Money Ladder G30 |
| **Small spends that add up** (`leaks.small_repeats`) | The same small payment in a **Want** category 4+ times in the month (Needs like matatu fares are never called leaks) | "Coffee 11 times = KSh 3,700, about KSh 44,000 a year at this pace." **A choice, not a crime.** Ask if it's worth it to them, and never call it waste |
| **Repeating payments** (`leaks.repeating_payments`) | Same payee and amount in 2+ months. Wants are listed first | "Showmax KSh 1,100 every month (KSh 13,200 a year). Still using it?" Needs like rent are fixed costs, not leaks |
| **Pace** (`pace`) | Mid-month: where each category is heading, based on their usual pattern. Ended month: plan vs actual | "Day 12 of 30 and 71% of your spending plan is gone. At this pace Groceries ends about KSh 3,300 over." Skip it when `too_early` (before day 7). Name `unplanned` categories so they can add them to My Budget |
| **What-ifs** (`what_ifs`) | Moving X a month from a category to the emergency fund, each goal, or extra loan payments | "Move KSh 2,000 a month from Eating out: emergency fund full in 21 months instead of 35, or the Laptop in 18 instead of 35, or debt-free 2 months sooner with KSh 450 less interest." Offer 2-3 amounts they pick; they choose where it goes. Ask permission before running a what-if on a Need |
| **Cash crunch** (`cash_crunch`) | Bills due before the main income arrives (due days from the Profile) | "Rent (5th) and Wi-Fi (3rd) are due before your salary (25th): KSh 21,000 that has to come from last month's money." Suggest keeping it aside on payday, or asking to move a due date. If `bills_missing_due_day`, ask for the due days |
| **Payday pattern** (`patterns`) | Share of the month's spending in the 5 days after payday; the busiest day | "About a quarter of your spending happens in the 5 days after payday." Tip: pay yourself first, moving savings out on payday before spending starts |
| **Health check** (`health`) | Month by month: savings rate, debt payments ÷ income, fees ÷ spending, needs/wants/future; emergency months now | Show it as a small table with arrows (↑ ↓ →) against the guides. A month still in progress has no ratios. Say what improved first |
| **Investing readiness** (`investing`) | Ladder step; money sitting in spending accounts beyond one month of essentials | Before step 4: "Investing comes after the buffer and expensive debt. Here's why." From step 4: explain options (money market funds, T-bills, SACCOs, bonds) and their trade-offs in simple words. Get current rates (see `money-math.md`). **Never name a fund, provider or product to buy** |

## 3. Formats

**Before any check-in**, look at `log_checks` and `pace.plan_looks_off`. Mention possible duplicates or a plan far from what they really pay in one line, as "worth a look". Never delete or change their rows. If a plan looks off, say the totals that use it may be off too.

**Weekly check-in** (scheduled email or chat, 6-8 lines):
1. Coverage and rows added this week.
2. Money in and out this week (`week`: the 7 days up to today), and pace for the month (one line).
3. The one category heading over, or "on track".
4. One leak or repeating payment worth a look.
5. Cash crunch warning from `cash_crunch.upcoming`: bills not yet paid this month that fall due before the main income arrives.
6. Ladder step and one next move.

**Month letter** (after the Month-End Check, about 5 lines, warm and plain; built from `letter_facts` plus the rest):
- One thing that went well (always first).
- The biggest leak, as a question.
- The health check trend in one sentence.
- One what-if worth trying next month.
- Ladder step and next move. Offer short answers to copy into the reflections at the bottom of Month-End Check.

**Insights on request:** lead with the single most useful finding, then up to 3 more. End with one question: "Want to see what moving KSh 2,000 a month would do?"

## 4. Dashboard (Claude Artifacts)

When they ask for a dashboard, or at the end of a month review, offer one. **Use the template, don't design a new one**: `assets/dashboard-template.html` is in the planner's style and its chart colours are already checked for colour-blind readers, in light and dark.

1. Get the facts as in section 1 (the `.xlsx`, or `data.json` from the Google Sheets ranges).
2. Build it: `python3 scripts/fnsoko_tools.py dashboard --data data.json --name "<first name, or leave out>" --out dashboard.html` (or `--planner PLANNER.xlsx`; add `--month 2026-10` for a finished month).
3. Show `dashboard.html` as an Artifact, exactly as built. Don't edit the HTML or the numbers.
4. Tell them, in one or two lines, what it shows and the one thing worth a look first.

It opens on **This month**. Tabs across the top add **Debt-free**, **Emergency fund**, **Goals**, **My year**, **Net worth** and **My future**; link straight to one with `#debt`, `#fund`, `#goals`, `#year`, `#worth` or `#future` at the end of the address, or just tell them which tab to open ("show me my debt-free plan" → the Debt-free tab). A tab with nothing in the planner yet says what to fill in.

What This month shows:
- status chips: coverage (VERIFIED / PROVISIONAL / ESTIMATED), Ladder step, day of the month
- four tiles: money in, money out, share saved, emergency fund in months
- spending against plan: one bar per category with a plan tick and, mid-month, where it's heading
- worth a look: bills due before income, pricey loans, fees, small repeat spends, repeating Wants, payday pattern, possible duplicates
- where your money goes: Needs / Wants / Future for each finished month, with a table view
- a what-if slider: move X a month → emergency fund, each goal, and loan payoff with interest saved

The other tabs:
- **Debt-free:** total owed, debt-free date, interest still to pay, each loan's true yearly cost, what to pay this month, and an extra-payment slider with Avalanche / Snowball
- **Emergency fund:** saved vs target with 1-month and full-fund marks, months covered, the date it's full, and its balance month by month
- **Goals:** a card per goal (progress, on track or not, amount a month, date), plus savings that have no target yet
- **My year:** money in and out by month, where most of it went, and the share saved each month
- **Net worth:** the planner's net worth by month, what they own and owe, and what they own by type
- **My future:** filled from My Future, with boxes they can change to explore (age, income wanted, monthly saving): pot in today's money, what it could pay, and what it takes to hit the target. Always an estimate

**Can't run code?** Fill the template by hand: replace the JSON between the `FNSOKO-DATA` markers with `{"name": "", "made": "YYYY-MM-DD", "insights": {...}}`, where `insights` follows the output of the `insights` command. If that isn't possible, use fallback prompt 12 and say the result is a one-off design.

It's a snapshot. Their planner stays their record, and the dashboard never asks for or shows names, phone numbers or account numbers.

## 5. Rules for this mode

- Every number comes from the script or their planner. Never estimate one for effect.
- Lead with what's going well. Leaks are information, not judgement.
- One to three suggestions at most. They choose; you never move money or change their budget without a yes.
- Never cut a real Need to make a what-if look good.
- No product picks (ground rule 8). For investing, explain; don't recommend.
