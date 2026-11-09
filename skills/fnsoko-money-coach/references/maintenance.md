# Keeping the skill and the planner in step

## Versions

- The planner stores its version in `Workings!C205` (now `FNSOKO-PLANNER-v5`). The script's `EXPECTED_VERSION` must match.
- **Any change that moves an input cell, renames a tab or changes a special category = a new version.** Bump both the planner cell and `EXPECTED_VERSION`, and update `tracker-map.md`.
- Older planners: the skill refuses to write and asks the person to get the latest planner. Their data can be copied across by hand (white boxes only).

## Before you release a change

1. `python3 tests/run_tests.py` (add `--planner NEW.xlsx` to test a new planner). Every check must pass.
2. With LibreOffice available, set `FNSOKO_RECALC` to recalculate the file, so the end-to-end check (Amina's October comes out VERIFIED) runs too.
3. Run the conversation checklist in `tests/README.md` by hand on one persona.
4. If you changed a prompt or an output format, update `fallback-prompts.md` and the Ask Claude prompts at the bottom of the planner's Start Here tab.

## Adding a new bank or statement format

1. Put an anonymised sample (fake names and amounts) in `tests/fixtures/statements/<name>/` via `make_fixtures.py`.
2. If the header uses new words, add them to `HEAD` in `scripts/fnsoko_tools.py`.
3. Add checks to `run_tests.py`, then run the tests.

## The starter rules list

- Every quarter, look at which payees people are asked about most (from the opt-in usage log or class feedback). Add common merchants to the planner's starter My Rules.
- Keep rules short and specific; more specific above more general (UBER EATS above UBER).
- Never add personal names to the starter list.

## The usage log (opt-in)

`python3 scripts/fnsoko_tools.py log --folder "My Money" --mode import --rows-auto 52 --questions 6 --step 2 --stuck "chama payout"`

It writes `fnsoko-usage-log.csv` in their folder: month, mode, counts, step, a few words on where they got stuck. No names, no amounts. Only with their yes. Fnsoko collects these only if the person chooses to share the file.
