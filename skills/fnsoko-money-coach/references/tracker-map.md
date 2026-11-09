# Fnsoko Money Planner map (version FNSOKO-PLANNER-v5)

White boxes = the person types. Everything else fills itself in. The version is stored in `Workings!C205`; the skill only writes to v5.

v5 has 17 tabs: Start Here (with the Ask Claude prompts at the bottom), My Money Ladder, My Money Profile, Setup, My Budget, Money Log, My Rules, This Month, Month-End Check (with the reflections at the bottom), My 50-30-20, My Year, My Net Worth, My Emergency Fund (deposits log at the bottom), My Goals (goal cards, then deposits log), My Loans (debt-free plan, then the month-by-month schedule), My Future, Workings (all the maths).

## How the tabs feed each other

- **Money Log** (the only daily input) feeds This Month, My Year, Month-End Check, My 50-30-20, My Emergency Fund, Goals and the net-worth auto rows.
- **Setup** (categories + Need/Want tags) feeds My Budget, the Money Log list, My Rules, and the 50/30/20 split.
- **My Budget** (Needs) feeds the emergency fund target.
- **My Loans** (the list at the top) feeds the debt-free plan and month-by-month schedule further down the same tab, the ladder's expensive-debt figure and My Net Worth (what I owe).
- **My Net Worth** (pension, shares) and average Future feed the hints on My Future.
- **All of the above** feed My Money Ladder (the 7 steps, current step, next move).

## Special Money Log categories (not income or spending)

| Category | Use for |
|---|---|
| Transfer between my accounts | Bank to M-Pesa, M-Pesa to bank, between their own wallets |
| Cash withdrawal | Agent or ATM cash (log the spending too if they know it) |
| From my emergency fund | Money taken back out of the emergency fund |
| From my savings | Chama payout, MMF / SACCO / M-Shwari withdrawal |
| Borrowed money | Fuliza draw, Tala or Branch disbursement, a loan from a person |

Savings into the emergency fund use the category chosen in My Emergency Fund H11 (default "Emergency fund"). Savings for a goal use a Savings category named exactly like the goal.

## Input cells

| Tab | Cells | What |
|---|---|---|
| My Money Ladder | G30 | Yearly rate from which a loan counts as expensive (default 20%) |
| My Money Profile | C6, F6 | Last checked, next check |
| | C15:G17 | Why, 90-day focus, 12-month goal |
| | B23:G28 | Income: Source, Regular/Variable, Usual month, Low month, How sure, Notes |
| | B34:G43 | Must pay: What, Amount each month, Due day, How sure, Notes (F:G merged) |
| | B49:G53 | Debts: Loan, Still owe, Monthly payment, Interest rate, How sure, Notes |
| | B59:G63 | Savings & goals: What for, Have now, Target, By when, How sure, Notes |
| | C67:G70, C74:G78 | Money rules; still to find out |
| Setup | C6, C7 | Year, currency |
| | B13:F27 | Categories: B Income, C Bills & Subscriptions, D Everyday, E Savings & Investments, F Debt Repayments (15 each, names unique) |
| | C36:C50, E36:E50 | Need/Want for each Bills and Everyday category (same order) |
| My Budget | C10:O24 / C29:O43 / C48:O62 / C67:O81 / C86:O100 | Income / Bills / Everyday / Savings / Debt; column C = usual each month, D..O = Jan..Dec overrides; rows follow Setup order |
| Money Log | B10:F2009 | Date, Category, Amount (positive), Note, Added by (Claude / Me / Checked); G fills itself |
| My Rules | B12:D311 | Words to look for, Category, Notes (E checks the category exists) |
| This Month | D6, J6 | Month to show, carry over Yes/No |
| Month-End Check | B16:P23 | Spending accounts: Account, Type, Start (1 Jan), Jan..Dec end-of-month balances (E..P) |
| | C28 | Small gap I'm OK with |
| | C57:K68, C73:K76 | Reflections: monthly (C priorities, F went well, I do better) and quarterly (C, F, I), each merged across 3 columns |
| My 50-30-20 | D6; E54, E55 | Month (empty = latest); extra income, share to Future |
| My Net Worth | B30:O42, B51:O59 | What I own / owe by month; rows 43, 44 and 60 fill themselves |
| My Emergency Fund | H8, H9, H10 | Months to cover (3-6), currency, where it's kept |
| | H11, H20 | Money Log category for the fund; use budget Needs (Yes/No) |
| | E15:E19, L15:L19 | Essentials if H20 = No |
| | B64:K363 | Deposits log: B Date, D What happened, F Amount, H Note (L fills itself). Only interest earned, or money in/out not on the Money Log |
| My Goals | E8, E9 | Currency, inflation |
| | C15:K26 | C What for, E How much, G By when, I Start date, K Inflation Yes/No (each merged over 2 columns except K) |
| | B94:M393 | Deposits log: B Date, D Which goal, G In/out, H Amount, J Note. Only withdrawals or money not on the Money Log |
| My Loans | H8:H11 | Currency, start month, extra a month, method (Avalanche / Snowball / My own order) |
| | C17:J24 | C Loan, E Lender, F Owe today, G Rate, H per year/per month, I Minimum, J My order |
| My Future | C6:C13 | Age, target age, monthly income wanted (today's money), saved today, added monthly, return, inflation, yearly spend share |

## Where people look

- "Where am I?": **My Money Ladder**
- "Did my month add up?": **Month-End Check**
- "Am I overspending on wants?": **My 50-30-20**
- "How long until my fund is full?": **My Emergency Fund**
- "When will I be debt-free?": **My Loans** (the plan under the loan list)
- "Am I on track to retire?": **My Future**
