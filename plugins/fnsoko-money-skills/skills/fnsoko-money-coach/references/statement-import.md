# Import statements ("update my planner")

Goal: turn M-Pesa and bank statements into Money Log rows, closing balances and new rules, asking the person only about what can't be sorted. The script does the reading and sorting the same way every time; you handle the conversation and the judgment calls.

## Folder the person keeps

```
My Money/
  Fnsoko_Money_Planner_2027.xlsx      (or the planner lives in Google Sheets)
  Statements/New/    <- drop new statements here (PDF, CSV or Excel)
  Statements/Done/   <- you move them here after importing
```

Unlocked files only. If a statement is password-protected, the person opens it and saves an unlocked copy (Print > Save as PDF). Never ask for the password.

## Steps

1. **Check the planner**
   `python3 scripts/fnsoko_tools.py check PLANNER.xlsx`. Stop if the version doesn't match.

2. **Read the statements**
   `python3 scripts/fnsoko_tools.py parse "My Money/Statements/New" --out /tmp/parsed.json`
   - **Import M-Pesa and bank statements together** (same folder) so moves between them are matched automatically.
   - The person's own name is found on the statement and removed. If it isn't (unusual layout), pass `--me "First Last"`.
   - Foreign currency: the output lists `NEEDS_RATE`. Ask "What rate should I use? For example, 1 GBP = 165 KES", then rerun with `--fx GBP=165`. Note the rate as ESTIMATED.
   - `LOCKED`, `NO_TEXT`, `NO_ROWS`: tell them the `what_to_do` text in plain words and continue with the other files.
   - The statement's period is in `statements`. If it is outside the planner's year, say so; those rows are not written.

3. **Sort**
   `python3 scripts/fnsoko_tools.py sort /tmp/parsed.json --planner PLANNER.xlsx --out /tmp/sorted.json [--month 2026-10]`
   - **First import: start with the last full month** (`--month`). A full M-Pesa statement often covers 3-6 months and 800+ rows. One month is about 200 rows and 25 questions, which is manageable. Do earlier months later, once My Rules has learnt their payees.
   This:
   - skips failed rows, duplicate statements and rows already on the Money Log
   - cancels reversals and refunds with the original
   - finds transfers between their own accounts
   - applies **My Rules** (first match wins, and the direction matters: a loan category on money in = Borrowed money; a savings category on money in = From my savings / From my emergency fund)
   - groups fees per account per month
   - lists `questions`, biggest first

4. **Ask** (max 3 questions per message, biggest first). Use `triage`:
   - Ask the `ask_now` questions first. They usually explain about 80-90% of the unsorted money.
   - Then offer: "There are 17 smaller groups left (78,775 in total). Shall we go through them, or put them under Miscellaneous for now?" Their choice.
   - **Merged questions** (`merged: true`, e.g. "24 different shops, one payment each"): show the 5 biggest items, and suggest a category for each from the shop name (e.g. Haru Restaurant → Eating out, Pharmaplus → Health & pharmacy). Ask them to confirm, then put the rest under one category. Record this with `split` (below).
   - **Money from or to a bank** (`... BANK`, `via API`, `Equity Paybill`, `I&M BANK C2B`) is usually their own account. Ask "Is this your own bank account?" If yes, use Transfer between my accounts, and tell them to add that bank account to the Month-End Check (or import its statement too). Otherwise the month can't come out VERIFIED.
   - **"Salary Payment from …" on M-Pesa** is how M-Pesa labels many payments from banks and companies, not proof of salary. Confirm before using Salary.
   - **Investment and SACCO lines** (Ziidi MMF, unit trusts, asset managers, SACCOs): money out goes to their savings category; money back in goes to From my savings. SACCO payments can also be loan repayments, so ask once.

   For each question, show who, how many times, the total and the suggested categories, then offer a rule: For each question show who, how many times, the total and the suggested categories, then offer a rule:

   > **1. JOHN K**: you paid him 6,500 in 3 payments (6 Oct to 20 Oct).
   > Is that Family support, Rent, Gifts & celebrations, or something else?
   > Should I always use that for JOHN K?

   - Big items (`big: true`) always get asked about, even if they look obvious.
   - `refund?` questions: "Was this money back for something you bought?" If yes, answer `Refund (cancel the purchase)`.
   - Merged questions ("8 different payers"), usually customers: "Are these customers paying your business?"
   - Chama: money out to the chama goes to the **Chama** savings category; a payout coming in goes to **From my savings**.
   - "I don't know" goes to **Miscellaneous** with Note CHECK. Don't push.
   - If they reply in a sentence, map it to the nearest category yourself and confirm in one line.

5. **Record the answers** in `/tmp/answers.json`:
   ```json
   {"answers": [{"id": "q1", "category": "Family support", "always": true},
                {"id": "q2", "category": "Emergency fund", "always": true, "keyword": "CIC MONEY MARKET"}],
    "account_map": {"Equity": "Main bank"}}
   ```
   - Merged question with different categories per item:
     `{"id": "q7", "category": "Miscellaneous", "split": [{"note_contains": "HARU", "category": "Eating out", "always": true}]}`
   - `keyword` is optional (the default is the payee shown). Choose a short, specific phrase from the statement that won't catch other payments.
   - `account_map` matches statement accounts to Month-End Check rows. If you don't set it, the tool matches by name, then by type ("Main bank"), then uses an empty row.

6. **Write**
   - If you can edit the planner file: `python3 scripts/fnsoko_tools.py write /tmp/sorted.json --planner PLANNER.xlsx --answers /tmp/answers.json --out "PLANNER (updated).xlsx"`. Only overwrite the original (`--in-place`) if the person said yes.
   - Google Sheets, or no file access: `python3 scripts/fnsoko_tools.py export /tmp/sorted.json --answers /tmp/answers.json` gives three paste-ready blocks: Money Log rows (paste at column B of the first empty row), new My Rules rows, and closing balances to type on the Month-End Check.

7. **Tidy up.** Move the imported files to `Statements/Done`. Delete `/tmp` files.

8. **Report** in 4 lines:
   - "Added 58 rows: 52 sorted automatically, 6 from your answers. 2 new rules saved."
   - "Money in 95,000 · out 71,300."
   - "October: VERIFIED ✅" (or PROVISIONAL with the amount not logged, or ESTIMATED if balances are missing). Check the planner's Month-End Check; never claim VERIFIED yourself.
   - "You're on step 2 (starter buffer). Next: save 8,500 more into your emergency fund."

   Remind them: "Rows marked Claude: have a quick look, then change them to Checked."

## When the script can't help

- **A bank format it can't read:** ask for the CSV or Excel download, or read the table yourself and produce rows in the same 5 columns. Label them ESTIMATED until checked.
- **No statements, only memory:** use the Money Profile interview instead.
- **Cash spending:** statements can't see it. Ask for a rough weekly cash figure and log it as ESTIMATED under their usual categories.

## Never

- Change amounts, or invent rows to make totals match.
- Keep names, phone numbers, account numbers or receipt codes in notes or rules. The tools strip them; don't add them back.
- Write outside the white input boxes, or touch the Workings tabs.
