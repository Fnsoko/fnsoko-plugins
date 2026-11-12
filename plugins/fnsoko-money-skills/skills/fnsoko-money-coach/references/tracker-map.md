# Fnsoko Money Planner map (version FNSOKO-PLANNER-v5)

White boxes = the person types. **Green boxes fill themselves** from My Money Profile (see below). Everything else fills itself in. The version is stored in `Workings!C205`; the skill writes to the current and previous versions (see SKILL.md).

v5 has 17 tabs (the SMS-ready copy adds an 18th, SMS Inbox, after Money Log): Start Here (with the Ask Claude prompts at the bottom), My Money Ladder, Setup, My Money Profile, My Budget, Money Log, My Rules, This Month, Month-End Check (with the reflections at the bottom), My 50-30-20, My Year, My Net Worth, My Emergency Fund (deposits log at the bottom), My Goals (goal cards, then deposits log), My Loans (debt-free plan, then the month-by-month schedule), My Future, Workings (all the maths).

## How the tabs feed each other

- **Money Log** (the only daily input) feeds This Month, My Year, Month-End Check, My 50-30-20, My Emergency Fund, Goals and the net-worth auto rows.
- **Setup** (categories + Need/Want tags) feeds the My Money Profile lists, My Budget, the Money Log list, My Rules, and the 50/30/20 split.
- **My Budget** (Needs) feeds the emergency fund target.
- **My Loans** (the list at the top) feeds the debt-free plan and month-by-month schedule further down the same tab, the ladder's expensive-debt figure and My Net Worth (what I owe).
- **My Net Worth** (pension, shares) and average Future feed the hints on My Future.
- **All of the above** feed My Money Ladder (the 7 steps, current step, next move).

## Boxes that fill themselves from My Money Profile (green)

The Profile is where people type. These boxes hold formulas that copy from it. Planners copied before November 2026 are also v5 but may not have these links yet, so **check whether a cell holds a formula before writing**. If it does, write to the Profile instead.

| Tab | Cells | Comes from (My Money Profile) |
|---|---|---|
| My Budget | Column C rows that match a Profile name: Income, Bills, Everyday, Debt | Income B23:D28 (usual month), Must pay B34:C43, Money I owe B49:D53 (monthly payment), matched by Setup category name |
| My Money Profile | D59 (emergency fund target) | My Emergency Fund target (months x essentials) |
| My Emergency Fund | E15:E19, L15:L19 (essentials, used when H20 = No) | Must pay rows by category; L16 = loan payments; L19 = the rest |
| My Emergency Fund | Row 64 of the deposits log | C59 "Have now", dated with C6 "Last checked" |
| My Goals | C, E, G of rows 15-18 | Goals B60:E63 (what for, target, by when) |
| My Goals | Rows 94-97 of the deposits log | Goals C60:C63 "Have now" |
| My Loans | C, F, G, H, I of rows 17-21 | Money I owe B49:E53; H = "per month" when the Profile's last column (G49:G53) mentions month or mwezi |
| My Future | C9, C10 | My Net Worth (pension + shares & bonds), average Future savings on the Money Log. People may type over these |
| My Emergency Fund, My Goals, My Loans | H9, E8, H8 (currency) | Setup C7 |
| My Loans | H9 (plan start month) | Month of C6 "Last checked", or January of the Setup year |
| My Net Worth | Rows 30-31, Jan..Dec | Month-End Check accounts (B16:P23): row 30 = M-Pesa and Cash types, row 31 = all other accounts |

Typed rows start after the linked ones: My Net Worth rows 32-42, My Goals rows 19-26, My Loans rows 22-24, deposit logs from row 65 (emergency fund) and row 98 (goals). Spending-account balances are typed once, on Month-End Check.

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
| | B49:G53 | Debts: Loan, Still owe, Monthly payment, Interest rate, How sure, Per year or per month? / Notes (dropdown, free text allowed) |
| | B59:G63 | Savings & goals: What for (B60:B63 dropdown from Setup Savings categories), Have now, Target (D59 fills itself), By when, How sure, Notes |
| | C67:G70, C74:G78 | Money rules; still to find out |
| Setup | C6, C7 | Year, currency |
| | B13:F27 | Categories: B Income, C Bills & Subscriptions, D Everyday, E Savings & Investments, F Debt Repayments (15 each, names unique) |
| | C36:C50, E36:E50 | Need/Want for each Bills and Everyday category (same order) |
| My Budget | C10:O24 / C29:O43 / C48:O62 / C67:O81 / C86:O100 | Income / Bills / Everyday / Savings / Debt; column C = usual each month, D..O = Jan..Dec overrides; rows follow Setup order |
| Money Log | B10:F2009 | Date, Category, Amount (positive), Note, Added by (Claude / Me / Checked); G fills itself |
| SMS Inbox *(SMS-ready planner only)* | B7:D | Received (filled by the script), Message (raw SMS, filled by the script), Logged (you: a date, or `Skipped: reason`). Header on row 6. No formula reads this tab, so the planner version stays v5. See `sms-inbox.md` |
| My Rules | B12:D311 | Words to look for, Category, Notes (E checks the category exists) |
| This Month | D6, J6 | Month to show, carry over Yes/No |
| Month-End Check | B16:P23 | Spending accounts: Account, Type, Start (1 Jan), Jan..Dec end-of-month balances (E..P) |
| | C28 | Small gap I'm OK with |
| | C57:K68, C73:K76 | Reflections: monthly (C priorities, F went well, I do better) and quarterly (C, F, I), each merged across 3 columns |
| My 50-30-20 | D6; E54, E55 | Month (empty = latest); extra income, share to Future |
| My Net Worth | B32:O42, B51:O59 | What I own / owe by month; rows 30, 31, 43, 44 and 60 fill themselves |
| My Emergency Fund | H8, H10 | Months to cover (3-6), where it's kept (H9 currency follows Setup) |
| | H11, H20 | Money Log category for the fund; use budget Needs (Yes/No) |
| | E15:E19, L15:L19 | Essentials if H20 = No |
| | B65:K363 | Deposits log: B Date, D What happened, F Amount, H Note (L fills itself). Only interest earned, or money in/out not on the Money Log. Row 64 = starting balance from the Profile |
| My Goals | E9 | Inflation (E8 currency follows Setup) |
| | C15:K26 | C What for, E How much, G By when, I Start date, K Inflation Yes/No (each merged over 2 columns except K) |
| | B98:M393 | Deposits log: B Date, D Which goal, G In/out, H Amount, J Note. Only withdrawals or money not on the Money Log. Rows 94-97 = starting balances from the Profile |
| My Loans | H10, H11 | Extra a month, method (Avalanche / Snowball / My own order). H8 currency and H9 start month fill themselves |
| | C17:J24 | C Loan, E Lender, F Owe today, G Rate, H per year/per month, I Minimum, J My order |
| My Future | C6:C13 | Age, target age, monthly income wanted (today's money), saved today, added monthly, return, inflation, yearly spend share |

## Where people look

- "Where am I?": **My Money Ladder**
- "Did my month add up?": **Month-End Check**
- "Am I overspending on wants?": **My 50-30-20**
- "How long until my fund is full?": **My Emergency Fund**
- "When will I be debt-free?": **My Loans** (the plan under the loan list)
- "Am I on track to retire?": **My Future**
