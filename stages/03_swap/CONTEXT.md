# 03_swap - run the Altium script on approved projects

One job: build the job list for the approved projects and have the Altium script swap their templates.

## Inputs
- Working (this run): `../02_plan/output/<slug>/plan.csv` for each approved project
- Working (this run): `../01_inventory/output/<slug>/inventory.json` for each approved project
- Reference (every run): `../../_shared/template-map.md`
- Reference (every run): `../../_shared/altium-steps.md`

Do NOT load: other projects' output, stage 04's files except to skip a passing slug, the old `.SchDoc` files.

## Process
1. If an input is missing, stop and say which. Drop any approved slug whose `../04_verify/output/<slug>/check.md` already starts with `pass`.
2. Run `python _tools/make_jobs.py <templates folder from template-map.md> <slug> [<slug> ...]`. If it refuses, report the file it names and stop.
3. Tell you: back up or work on copies, then in Altium use File > Run Script, browse to `_tools/altium/RebrandTemplates.pas`, and run `RunBatch`. This needs the pilot passed first (see prerequisites).
4. When you say it finished, read `output/swap-log.txt` and report the FAIL and NOTE lines. If the script is unusable, offer the manual fallback steps in each project's run sheet.

## Outputs
- `jobs.txt`, `swap-log.txt` -> `output/` (one pair per batch, overwritten each time)

## Check
The last line of `swap-log.txt` is `DONE <n> ok, 0 failed`. Anything else stops the run and Claude reports the FAIL lines.
