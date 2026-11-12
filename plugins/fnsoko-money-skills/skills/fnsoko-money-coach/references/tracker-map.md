# Fnsoko Money Planner map (version FNSOKO-PLANNER-v6)

White boxes = the person types. **Green boxes fill themselves** from My Money Profile (see below). Everything else fills itself in. The version is stored in `Workings!C205`; the skill writes to the current and previous versions (see SKILL.md).

v6 has 17 tabs (the SMS-ready copy adds an 18th, SMS Inbox, after Money Log): Start Here (with the Ask Claude prompts at the bottom), My Money Ladder, Setup, My Money Profile, My Budget, Money Log, My Rules, This Month, Month-End Check (with the reflections at the bottom), My 50-30-20, My Year, My Net Worth, My Emergency Fund (deposits log at the bottom), My Goals (goal cards, then deposits log), My Loans (debt-free plan, then the month-by-month schedule), My Future, Workings (all the maths).

## How the tabs feed each other

- **Money Log** (the only daily input) feeds This Month, My Year, Month-End Check, My 50-30-20, My Emergency Fund, Goals and the net-worth auto rows.
- **Setup** (categories + Need/Want tags) fills the My Money Profile name columns (v6), My Budget, the Money Log list, My Rules, and the 50/30/20 split.
- **My Budget** (Needs) feeds the emergency fund target.
- **My Loans** (the list at the top) feeds the debt-free plan and month-by-month schedule further down the same tab, the ladder's expensive-debt figure and My Net Worth (what I owe).
- **My Net Worth** (pension, shares) and average Future feed the hints on My Future.
- **All of the above** feed My Money Ladder (the 7 steps, current step, next move).

## Boxes that fill themselves from My Money Profile (green)

The Profile is where people type amounts. These boxes hold formulas that copy from it. Older v5 copies may not have all these links, so **check whether a cell holds a formula before writing**. If it does, write to the Profile (or, for a name, to Setup) instead.

| Tab | Cells | Comes from (My Money Profile) |
|---|---|---|
| My Money Profile | Name columns B23:B37, B43:B72, B78:B85, B92:B103 | Setup, in order, blanks skipped: income B13:B27; every Bills/Everyday category tagged Need (B36:E50); debt F13:F27 (first 8); savings E13:E27 except the emergency fund name in B91 (first 12) |
| My Budget | Column C rows that match a Profile name: Income, Bills, Everyday, Debt | Income B23:D37 (usual month), Must pay B43:C72, Money I owe B78:D85 (monthly payment), matched by Setup category name |
| My Money Profile | D91 (emergency fund target) | My Emergency Fund target (months x essentials) |
| My Emergency Fund | E15:E19, L15:L19 (essentials, used when H20 = No) | Must pay rows by category; L16 = loan payments; L19 = the rest |
| My Emergency Fund | Row 64 of the deposits log | C91 "Have now", dated with C6 "Last checked" |
| My Goals | C, E, G of rows 15-26 (goal n = Profile row 91+n) | Goals B92:E103, only rows with Have now, Target or By when filled, so gaps are normal |
| My Goals | Rows 94-105 of the deposits log | Goals C92:C103 "Have now" |
| My Loans | C, F, G, H, I of rows 17-24 (loan n = Profile row 77+n) | Money I owe B78:E85, only rows with What I owe or Monthly payment filled, so gaps are normal; H = "per month" when the Profile's last column (G78:G85) mentions month or mwezi |
| My Future | C9, C10 | My Net Worth (pension + shares & bonds), average Future savings on the Money Log. People may type over these |
| My Emergency Fund, My Goals, My Loans | H9, E8, H8 (currency) | Setup C7 |
| My Loans | H9 (plan start month) | Month of C6 "Last checked", or January of the Setup year |
| My Net Worth | Rows 30-31, Jan..Dec | Month-End Check accounts (B16:P23): row 30 = M-Pesa and Cash types, row 31 = all other accounts |

Typed rows start after the linked ones: My Net Worth rows 32-42, deposit logs from row 65 (emergency fund) and row 106 (goals). In v6 every My Goals and My Loans row is linked. Spending-account balances are typed once, on Month-End Check.

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
| | C23:G37 | Income (15 rows): Regular/Variable, Usual month, Low month, How sure, Notes. B = name from Setup |
| | C43:G72 | Must pay (30 rows): Amount each month, Due day, How sure, Notes (F:G merged). B = name from Setup |
| | C78:G85 | Debts (8 rows): Still owe, Monthly payment, Interest rate, How sure, Per year or per month? / Notes (dropdown, free text allowed). B = name from Setup |
| | B91:G103 | Savings & goals: row 91 = emergency fund (B typed, D fills itself); rows 92-103 = goals, B from Setup. C Have now, D Target, E By when, F How sure, G Notes |
| | C107:G110, C114:G118 | Money rules; still to find out |
| | (v5) | v5 Profile rows: income 23-28, must pay 34-43, debts 49-53, goals 59-63, rules 67-70, still to find out 74-78; names typed or picked from dropdowns |
| Setup | C6, C7 | Year, currency |
| | B13:F27 | Categories: B Income, C Bills & Subscriptions, D Everyday, E Savings & Investments, F Debt Repayments (15 each, names unique) |
| | C36:C50, E36:E50 | Need/Want for each Bills and Everyday category (same order) |
| My Budget | C10:O24 / C29:O43 / C48:O62 / C67:O81 / C86:O100 | Income / Bills / Everyday / Savings / Debt; column C = usual each month, D..O = Jan..Dec overrides; rows follow Setup order |
| Money Log | B10:F2009 | Date, Category, Amount (positive), Note, Added by (Claude / Me / Checked); G fills itself |
| SMS Inbox *(SMS-ready planner only)* | B7:D | Received (filled by the script), Message (raw SMS, filled by the script), Logged (you: a date, or `Skipped: reason`). Header on row 6. No formula reads this tab, so it never changes the planner version. See `sms-inbox.md` |
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
| | B106:M393 | Deposits log: B Date, D Which goal, G In/out, H Amount, J Note. Only withdrawals or money not on the Money Log. Rows 94-105 = starting balances from the Profile (v5: rows 94-97, typed from row 98) |
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
