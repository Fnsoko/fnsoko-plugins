# Fnsoko Money Planner map (version FNSOKO-PLANNER-v7)

**v7 (Dec 2026) in one line:** up to 50 categories per group on Setup, Need/Want picked beside each Bills and Everyday name, longer lists on My Money Profile and My Budget (names there are plain text the script keeps in step with Setup), Money Log to row 10,009, and a "Bring in my old planner" menu. Cells below are v7; **v6 differences are in the section "v6 (previous version)" at the end.** Check `Workings!C205` first.

White boxes = the person types. **Green boxes fill themselves** from My Money Profile (see below). Everything else fills itself in. The version is stored in `Workings!C205`; the skill writes to the current and previous versions (see SKILL.md).

v7 has 18 tabs (v6: 17, plus SMS Inbox in the SMS-ready copy): Start Here (with the "Let AI help you fill this in" prompts at the bottom, B76:C99; before 15 Nov 2026 the section was "Ask Claude (optional)"), My Money Ladder, Setup, My Money Profile, My Budget, Money Log, My Rules, This Month, Month-End Check (with the reflections at the bottom), My 50-30-20, My Year, My Net Worth, My Emergency Fund (deposits log at the bottom), My Goals (goal cards, then deposits log), My Loans (debt-free plan, then the month-by-month schedule), My Future, Workings (all the maths).

**Planner additions (14 Nov 2026, still v6):** Start Here has a "first 10 minutes" box and a tab picker (named range `FnsokoTabPicker`, Start Here D32; works on the phone app). My Money Profile has a payslip calculator at the bottom (v7: gross C188, result B189 (ESTIMATED), rates C192 NSSF upper limit, C193 SHIF, C194 housing levy, C195 personal relief; v6: C123, B124, C127:C130). My Budget B7 shows the plan's split, the Future step and money to set aside for bigger months. Message lines now give amounts and dates: My Emergency Fund B28, My Goals B37 (goals need vs average saving), My Loans B35, My Net Worth B9 and M6:M7 (change since last month), My Year B9 (savings at this pace). The script menu also has weekly and month-end emails (one switch: Fnsoko > Email me weekly and month-end updates) and "Start my next year's planner" (copies the file, carries balances, goal savings, fund, net worth items; Money Log starts empty).

**Doubles (14 Nov 2026):** Money Log G6:G7 "Possible doubles" = rows with the same date and amount where one is Added by SMS and one isn't; those rows are highlighted yellow. Month-End Check messages now say a gap can also mean something was logged twice.

**Plain words in the planner (14 Nov 2026):** Month-End Check shows "✅ Adds up" / "Something's missing" / "Not checked yet" (I7, J31:J42) where older copies say VERIFIED / PROVISIONAL / ESTIMATED; they mean the same. Use the planner's words with the person. "Essentials" is now "must-pay costs" on My Emergency Fund and the Money Ladder. Start Here folds "More on how it works", most tips and the Ask Claude prompts (click + on the left); My Money Profile folds "Still to find out" and the payslip rates.

**Hidden tabs (template from 14 Nov 2026):** a new copy opens with only Start Here, Setup, My Money Profile, My Budget, Money Log and This Month showing. The rest are hidden, not removed: their formulas still work and the Sheets connector still reads them. SMS Inbox and My Rules show themselves when the first SMS arrives; Workings stays hidden. When you send someone to a hidden tab, tell them how to see it: **Fnsoko (top menu) > Show all my tabs** (or Show my month-end tabs / Show my savings and debt tabs), or the **☰** button at the bottom left, then the tab name.

## How the tabs feed each other

- **Money Log** (the only daily input) feeds This Month, My Year, Month-End Check, My 50-30-20, My Emergency Fund, Goals and the net-worth auto rows.
- **Setup** (categories + Need/Want tags) fills the Money Log list, My Rules and the 50/30/20 split straight away. The names on **My Money Profile and My Budget** follow through the planner's script ("Tidy my lists"), which runs when the person edits Setup, when the planner opens, after Sort my SMS now, and from **Fnsoko > Tidy my lists**. Edits you make through the Sheets connector don't run it: after you add, rename or remove a category on Setup, ask the person to click **Fnsoko > Tidy my lists** (or reload the planner), then read the Profile and Budget again before writing amounts.
- **Tidy my lists in short:** a new Setup name goes into the first empty row of its section; a rename keeps the row and its amounts (and renames matching Money Log, My Rules and fund-category cells); a removed name with no amounts is cleared, one with amounts stays as **⚠️ name** so nothing is lost (⚠️ rows are left out of the Profile totals). Empty rows are hidden.
- **My Budget** (Needs) feeds the emergency fund target.
- **My Loans** (the list at the top) feeds the debt-free plan and month-by-month schedule further down the same tab, the ladder's expensive-debt figure and My Net Worth (what I owe).
- **My Net Worth** (pension, shares) and average Future feed the hints on My Future.
- **All of the above** feed My Money Ladder (the 7 steps, current step, next move).

## Boxes that fill themselves from My Money Profile (green)

The Profile is where people type amounts. These boxes hold formulas that copy from it. Older v5 copies may not have all these links, so **check whether a cell holds a formula before writing**. If it does, write to the Profile (or, for a name, to Setup) instead.

| Tab | Cells | Comes from (My Money Profile) |
|---|---|---|
| My Money Profile | Name columns B23:B72, B78:B137, B143:B150, B157:B168 | Plain text kept in step with Setup by the script (dropdowns allow picking): income = Setup B; must pay = every Bills/Everyday name tagged Need; debts = Setup H (first 8); goals = Setup G except the emergency fund name in B156 (first 12) |
| My Budget | Column C rows that match a Profile name: Income, Bills, Everyday, Debt | Income B23:D72 (usual month), Must pay B78:C137, Money I owe B143:D150 (monthly payment), matched by name. A green box someone typed over turns **orange** and My Budget B7 says so; pressing Delete links it back |
| My Money Profile | D156 (emergency fund target) | My Emergency Fund target (months x essentials) |
| My Emergency Fund | E15:E19, L15:L19 (essentials, used when H20 = No) | Must pay rows by category; L16 = loan payments; L19 = the rest |
| My Emergency Fund | Row 64 of the deposits log | C156 "Have now", dated with the planner start (Workings AH2) |
| My Goals | C, E, G of rows 15-26 (goal n = Profile row 156+n) | Goals B157:E168, **only rows with a Target or a By when** (savings with only "Have now", like a money market fund, are not goals), so gaps are normal |
| My Goals | Rows 94-105 of the deposits log | Goals C157:C168 "Have now", dated with the planner start |
| My Loans | C, F, G, H, I of rows 17-24 (loan n = Profile row 142+n) | Money I owe B143:E150, only rows with What I owe or Monthly payment filled, so gaps are normal; H = "per month" when the Profile's last column (G143:G150) mentions month or mwezi |
| My Future | C9, C10 | My Net Worth (pension + shares & bonds), average Future savings on the Money Log. People may type over these |
| My Emergency Fund, My Goals, My Loans | H9, E8, H8 (currency) | Setup C7 |
| My Loans | H9 (plan start month) | Planner start, Workings AH2 = month of C6 "Last checked", or this month while C6 is empty. The first amount typed on the Profile fills C6 with today; when you fill the Profile, fill C6 too |
| My Net Worth | Rows 30-31, Jan..Dec | Month-End Check accounts (B16:P23): row 30 = M-Pesa and Cash types, row 31 = all other accounts |

Typed rows start after the linked ones: My Net Worth rows 32-42, deposit logs from row 65 (emergency fund) and row 106 (goals). In v6 and v7 every My Goals and My Loans row is linked. Spending-account balances are typed once, on Month-End Check.

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
| | C23:G72 | Income (50 rows): Regular/Variable, Usual month, Low month, How sure, Notes. B = name (follows Setup) |
| | C78:G137 | Must pay (60 rows): Amount each month, Due day, How sure, Notes (F:G merged). B = name (follows Setup) |
| | C143:G150 | Debts (8 rows): Still owe, Monthly payment, Interest rate (**type it as a percentage, like 4% or 18%**: the box takes 0% to 200%), How sure, Per year or per month? / Notes (dropdown, free text allowed). B = name (follows Setup) |
| | B156:G168 | Savings & goals: row 156 = emergency fund (B typed, D fills itself); rows 157-168 = goals, B follows Setup. C Have now, D Target, E By when, F How sure, G Notes |
| | C172:G175, C179:G183 | Money rules; still to find out |
| | C188; B189; C192:C195 | Payslip calculator: gross; result (ESTIMATED); rates (NSSF upper limit, SHIF, housing levy, personal relief) |
| | Rows whose name starts with ⚠️ | A category removed from Setup that still has amounts. Don't write to them; ask the person whether to clear the amounts or put the name back on Setup |
| Setup | C6, C7 | Year, currency |
| | B13:H62 | Categories, up to 50 per group, names unique: B Income, C Bills & Subscriptions, **D Need/Want for C**, E Everyday Expenses, **F Need/Want for E**, G Savings & Investments, H Debt Repayments. To add one, type it in the first empty white box of its column (a new Bills name defaults to Need, a new Everyday name to Want: ask which it is). B11 warns when a group is full or a name sits past row 62 (not counted) |
| My Budget | C10:O59 / C64:O113 / C118:O167 / C172:O221 / C226:O275 | Income / Bills / Everyday / Savings / Debt (50 rows each); B = name (follows Setup, plain text); column C = usual each month (green when linked to the Profile), D..O = Jan..Dec overrides; P = year, worked out on the row. Skip ⚠️ rows |
| Money Log | B10:F10009 | Date, Category, Amount (positive), Note, Added by (Claude / Me / Checked / SMS: added by the planner's SMS sorter); G fills itself |
| SMS Inbox *(SMS-ready planner only)* | B7:D | Received (filled by the script), Message (raw SMS, filled by the script), Logged (you: a date, or `Skipped: reason`). Header on row 6. No formula reads this tab, so it never changes the planner version. See `sms-inbox.md` |
| My Rules | B12:D311 | Words to look for, Category, Notes (E checks the category exists) |
| This Month | D6, J6 | Month to show, carry over Yes/No |
| Month-End Check | B16:P23 | Spending accounts: Account, Type, Start (1 Jan), Jan..Dec end-of-month balances (E..P) |
| | C28 | Small gap I'm OK with |
| | C57:K68, C73:K76 | Reflections: monthly (C priorities, F went well, I do better) and quarterly (C, F, I), each merged across 3 columns |
| My 50-30-20 | D6; D12; E56, E57 | Month (empty = latest); Future step for now (empty = suggested, Workings AG171; in use AG172); extra income, share to Future |
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

## Planner menu (Fnsoko, top of the sheet)

v7 adds **Tidy my lists** (brings My Budget and the Profile in step with Setup) and **Bring in my old planner** (in a fresh v7 copy: copies everything from a v6 planner and checks each month's totals match). Moving someone to v7 = they make a copy of the latest planner, open it, and run Bring in my old planner with their old planner's link. Never move their numbers by hand cell by cell when the menu can do it.

## Where people look

- "Where am I?": **My Money Ladder**
- "Did my month add up?": **Month-End Check**
- "Am I overspending on wants?": **My 50-30-20**
- "How long until my fund is full?": **My Emergency Fund**
- "When will I be debt-free?": **My Loans** (the plan under the loan list)
- "Am I on track to retire?": **My Future**

## v6 (previous version)

Same tabs and the same cells everywhere except:

- **Setup** B13:F27, 15 per group: B Income, C Bills, D Everyday, E Savings, F Debt. Need/Want in a separate table: Bills names B36:B50 with tags C36:C50, Everyday names D36:D50 with tags E36:E50.
- **My Money Profile:** income C23:G37, must pay C43:G72, debts C78:G85, savings B91:G103 (91 = emergency fund, D91 target), money rules C107:G110, still to find out C114:G118, payslip gross C123 (rates C127:C130). Names fill themselves from Setup with formulas. Goal n = Profile row 91+n; loan n = Profile row 77+n. Savings with only "Have now" can show as goal cards.
- **My Budget:** C10:O24 / C29:O43 / C48:O62 / C67:O81 / C86:O100.
- **Money Log:** B10:F2009.
- **My Loans H9:** month of C6 "Last checked", or January of the Setup year when C6 is empty.
- No Tidy my lists or Bring in my old planner.
