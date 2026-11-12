# Keeping the skill and the planner in step

## Versions

- The planner stores its version in `Workings!C205` (now `FNSOKO-PLANNER-v5`). The script lists the versions it supports in `SUPPORTED_VERSIONS`, newest first.
- **Policy: the skill supports the current and the previous planner version**, so nobody is cut off the day a new planner comes out.
- **Prefer changes that keep the version.** Linking boxes with formulas, new help text, new dropdowns and extra tabs nothing reads (like SMS Inbox) all stay on the same version.
- **Any change that moves an input cell, renames a tab or changes a special category = a new version.** When you make one:
  1. Set the new version in the planner's `Workings!C205`.
  2. Add it at the front of `SUPPORTED_VERSIONS`, keep the previous version, and drop the one before that.
  3. Wherever the script reads or writes a cell that moved, branch on `info['version']`.
  4. Update `tracker-map.md`, noting where the previous version differs.
  5. Bump the plugin version and release, so marketplace installs update before people get the new planner.
- Planners older than both supported versions: the skill doesn't write to them. It coaches from what they show and offers to help copy the white boxes into the latest planner.

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
