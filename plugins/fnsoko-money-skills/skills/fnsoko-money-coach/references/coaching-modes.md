# Coaching modes

## §1 Money Profile interview (5 rounds)

Start from what they've already said. Up to 3 questions per round, the most important gaps first. If statements were imported, use them to turn ESTIMATED into KNOWN instead of asking.

| Round | Ask about |
|---|---|
| 1 The basics | Month and currency; take-home pay and pay day; other income and how often; main money challenge |
| 2 What must go out | Each bill and its amount; debts and required payments; people they support |
| 3 Everyday life | Food, transport, going out; subscriptions; unplanned spending (contributions, treats); automated savings |
| 4 What they have | Savings and investments and where; emergency fund; irregular income and a low month (check against a statement) |
| 5 Where they're going | One goal (amount, date, age if age-based); what happens to extra money; what they're open to (earn more, more risk, move dates) |

After **every** round:
1. Tables (money in, money out, what they own), with every figure labelled.
2. **The key number**: in minus out, and how much is unexplained.
3. One or two findings in plain words ("Bills are only 13% of income, so most money goes elsewhere").
4. New words explained.
5. "Still to check" list.
6. The next 3 questions.

If they say the rounds are done, stop asking. Then put the profile where it belongs:

- **Planner connected and on a supported version** (Google Sheets connector, or the file is open): show the final profile in My Money Profile's layout and ask "Shall I fill this in for you?". On a yes, write it into the Profile's **white boxes only** (cells in `tracker-map.md`, Input cells): Why I'm doing this (C15:C17), Money coming in (C:G of rows 23-72), Must pay (C:F of rows 78-137), Money I owe (C:G of rows 143-150, with "per month" or "per year" in G, and the rate as a percentage like 4%), Savings & goals (C:G of rows 157-168, plus C156 for what the emergency fund holds now), My money rules (C172:C175) and Still to find out (C179:C183). On a v6 planner the rows differ: see the v6 section of `tracker-map.md`. A name they need that isn't on the Profile yet: add it on Setup first (see `tracker-map.md`), ask them to run Fnsoko > Tidy my lists, then write the amounts. Leave a box empty when they gave no answer; never write a guess.
  - Match every line to the name already in column B. **Never type over column B, D91 or any formula.** If a name they need is not in column B, say which box to change on Setup (or offer to change it there), wait for the name to appear, then write its amounts.
  - Put KNOWN, ESTIMATED or UNKNOWN in each row's "How sure?" box.
  - Type today's date in **Last checked (C6)**, as a date like "16 Nov 2026". My Loans starts its debt-free plan from that month; left empty, the plan starts in January and the net worth line comes out wrong for anyone with a loan.
  - Afterwards read the four totals at the top back from the planner (usual money in, money in a low month, must pay + debt payments, left in a low month) and say them in one sentence, so the person can see it landed. Say which boxes you filled and which you left empty.
- **Not connected, an older or newer planner, or they would rather type it:** give the final profile in My Money Profile's layout, ready to type or paste.

Run these checks as facts arrive: the leak; emergency cover; whether stated income matches the assets behind it (e.g. bond size × rate ÷ 2 per payout); lumpy income turned into a monthly average, with a warning that it arrives in lumps.

## §2 Plan the month

1. Start from a **low month** of income. Variable income counts as 0 unless they give a realistic low figure.
2. Order: must-pay → minimum debt payments → savings and goals (emergency fund first) → everyday → buffer.
3. Every shilling gets a job. Show money left or the gap.
4. Never drop a required bill to make it fit. For a gap, give up to 3 choices.
5. Show the planned 50/30/20 split. Plan Future at least at their **Future step** (My 50-30-20 D12, or the suggestion), and show how far that is from the 20% guide, without pressure.
6. Output a table that matches My Budget's sections and their Setup categories. Label it ESTIMATED if any input is a guess. With the planner connected, show the table and ask before writing; on a yes, write the amounts into My Budget's white boxes (never the green ones: those come from My Money Profile, so change them there). Otherwise give the table to type in.

## §3 Month-end review

1. **Does it add up?** Use the planner's Month-End Check. If they imported statements, the balances for those accounts are already there (`statement-import.md` step 6): ask only for cash and accounts without a statement. VERIFIED, PROVISIONAL (with the amount not logged and where to look: small M-Pesa payments, fees, cash) or ESTIMATED (no balances). Never call a month verified yourself.
2. **Plan vs actual** where both exist. The 3 biggest differences.
3. **50/30/20, the Future step** and the **lifestyle check** (this month vs the 3 months before). Say Future against their step, then against the 20% guide, in shillings. If they reached their step two months in a row, suggest the next one (+3 points, up to 20%); they type it on My 50-30-20 D12 or leave it empty for the planner's suggestion. Needs over 50% are information, not something to cut. If Wants grew faster than income, name it as lifestyle creep, kindly.
4. **Ladder**: the step and one next move.
5. **Insights** (`insights.md`): run `insights --month YYYY-MM` and add the leaks, the health-check trend and one what-if. Close with the **month letter** (`insights.md` §3).
6. **One lesson, up to 3 actions with dates.** Short answers to copy into the reflections at the bottom of Month-End Check (priorities, what went well, what to do better).
7. **Raise or extra money coming?** Decide the split before it arrives (e.g. at least half to Future), using the raise planner on My 50-30-20.
8. **Life changed** (new job, loan, baby, move)? Update the profile: old value → new value, then which tabs to update.

## §4 Protect and grow

- **Starter buffer** (1 month of essentials) before attacking debt; the **full emergency fund** (3-6 months) after expensive debt is cleared.
- **Emergency fund:** it lives somewhere safe and quick to reach. Explain the options and how to check a provider is licensed; don't name one.
- **Debt:** list every loan with its rate and whether it's per month. Convert to yearly. Minimums on all; extra on the target loan. Avalanche (least interest) vs snowball (quick wins): they choose. My Loans does the schedule.
- **Goals:** monthly amount = (target − saved) ÷ months left. A goal named on My Goals plus a Savings category with the same name means Money Log savings count automatically.
- **Retirement / not needing to work:** use My Future. Explain the result: the pot in today's money, the income it could pay, the gap, and the extra needed each month. Show what changes with 5 more years or 10% more a month. Always ESTIMATED.
- **Long-term passive income goals** (e.g. "500,000 a month by 35"): convert to future money, work out the pot needed, compare paths (habits only, plug the leak, add income). Say honestly when saving alone can't close the gap, and name the levers: income, time, returns, target.
