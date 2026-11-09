# 01_inventory - read every sheet in a project

One job: record the size, current template, title-block state and parameters of every schematic sheet in one project.

## Inputs
- Working (this run): the `.PrjPcb` path (or folder) you were given
- Reference (every run): `../../CONTEXT.md` (for the project slug rule)

Do NOT load: `_shared/`, other stages, other projects' output.

## Process
1. If the path is missing, stop and say so. Work out `<slug>` by the rule in the root `CONTEXT.md`.
2. Run `python _tools/sch_inventory.py <path to .PrjPcb or folder> stages/01_inventory/output/<slug>`.
3. If the exit code is non-zero, list the sheets with an `error` and stop. Do not plan around a sheet that did not parse.

## Outputs
- `inventory.json` and `inventory.md` -> `output/<slug>/`

## Check
You confirm the sheet count matches the Projects panel in Altium and the sizes look right.
