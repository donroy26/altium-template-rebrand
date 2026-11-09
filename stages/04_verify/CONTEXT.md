# 04_verify - compare the project against the plan

One job: re-read the project from disk after the swap and confirm it matches the plan. It does not trust the script's log.

## Inputs
- Working (this run): `../01_inventory/output/<slug>/inventory.json`
- Working (this run): `../02_plan/output/<slug>/plan.csv`
- Reference (every run): `../../CONTEXT.md` (for the project slug rule)

Do NOT load: `_shared/`, the run sheet, the swap log, other projects' output.

## Process
1. If an input is missing, stop and say which. Confirm the swap ran, or that you saved after the manual fallback.
2. Run `python _tools/verify.py <path to .PrjPcb or folder> <slug>`.
3. Report the first line of `check.md`. A parameter listed as gone may be a planned rename from the template map; say so, do not hide it.
4. After a pass, tell you to open one sheet per size in Altium. The script cannot see whether the logo renders.

## Outputs
- `check.md`, `inventory.json`, `inventory.md` -> `output/<slug>/`

## Check
The script's `check.md`: first line `pass` or `fail: <why>`.
