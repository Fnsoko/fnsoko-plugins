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
| A file you can open (.xlsx) | `python3 scripts/fnsoko_tools.py insights --planner PLANNER.xlsx [--month 2026-11] [--whatif "Eating out:2000"]` |
| In Google Sheets (connector) | Read the ranges below, build `data.json` in the shape below, then run `insights --data data.json`. If you can't run code, follow the same steps by hand and label the results ESTIMATED |
| Not available | Ask them to paste this month's Money Log rows and their budget. Work from that only |

**Ranges to read in Google Sheets** (v6; v5 differences in brackets):
- Setup `B13:F27` (categories by group: B Income, C Bills, D Everyday, E Savings, F Debt) and `B36:E50` (Need/Want tags)
- Money Log `B10:E2009` (date, category, amount, note)
- My Budget `B10:O100` (B name, C usual, D..O = Jan..Dec)
- My Money Profile `B23:E37` income and `B43:D72` must-pay with due day in D (v5: `B23:E28`, `B34:D43`)
- Workings `C214` essentials, `C215` fund target, `C218` fund balance, `C196` ladder step, `B252:H263` goals (B name, D date, G target, H saved)
- My Loans `C17:I24` (C name, F owe, G rate, H per year/month, I minimum payment)
- Month-End Check `E16:P23` (balances, Jan..Dec) and `I31:I42` (not logged, Jan..Dec); My Emergency Fund `H11` (fund category); My Money Ladder `G30`

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
 "ladder_step": 2, "expensive_from": 0.2}
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

**Weekly check-in** (scheduled email or chat, 6-8 lines):
1. Coverage and rows added this week.
2. Money in and out this week, and pace for the month (one line).
3. The one category heading over, or "on track".
4. One leak or repeating payment worth a look.
5. Cash crunch warning if a big bill is due in the next 7 days before income.
6. Ladder step and one next move.

**Month letter** (after the Month-End Check, about 5 lines, warm and plain; built from `letter_facts` plus the rest):
- One thing that went well (always first).
- The biggest leak, as a question.
- The health check trend in one sentence.
- One what-if worth trying next month.
- Ladder step and next move. Offer short answers to copy into the reflections at the bottom of Month-End Check.

**Insights on request:** lead with the single most useful finding, then up to 3 more. End with one question: "Want to see what moving KSh 2,000 a month would do?"

## 4. Dashboard (Claude Artifacts)

When they ask for a dashboard, or at the end of a month review, offer one. Build an interactive Artifact from the insights facts:
- tiles for money in, money out, savings rate and emergency months
- spending by category against plan
- the health-check trend
- the leak list
- a what-if slider (amount a month → months to the fund or goal)

Use their currency. Make it readable on a phone, in light and dark. Use only figures from the facts, labelled with coverage. No names, phone numbers or account numbers. Tell them the dashboard is a snapshot; the planner stays their record.

## 5. Rules for this mode

- Every number comes from the script or their planner. Never estimate one for effect.
- Lead with what's going well. Leaks are information, not judgement.
- One to three suggestions at most. They choose; you never move money or change their budget without a yes.
- Never cut a real Need to make a what-if look good.
- No product picks (ground rule 8). For investing, explain; don't recommend.
