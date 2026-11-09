# 02_plan - choose templates and flag problems

One job: turn the inventory into a swap plan and a plan summary, with every problem flagged.

## Inputs
- Working (this run): `../01_inventory/output/<slug>/inventory.json`
- Reference (every run): `../../_shared/template-map.md`
- Reference (every run): `../../_shared/altium-steps.md`

Do NOT load: stages 03 and 04, other projects' output (except to rebuild the queue), the old `.SchDoc` files.

## Process
1. If an input is missing, or `template-map.md` still holds FILL, stop and say which.
2. Group the sheets by size. Pick each size's new template from the map. Write `plan.csv` with columns `sheet,size,new_template` (file name only).
3. Run `python _tools/sch_inventory.py <path to new .SchDot> stages/02_plan/output/<slug>/template-<name>` for each template used. Its `special_strings` are the title-block fields the new template shows.
4. Write `run-sheet.md`: the project path first, then a plan summary per size group (sheets, template file) and a Flags section. Add the manual click steps from `altium-steps.md`, labelled "fallback if the script cannot be used".
5. Flag: per sheet, a custom size, a size with no template in the map, no current template, and no template record with the built-in title block off (the old title block may be drawn on the sheet; the script cannot remove it, so it stays manual). Also flag a sheet whose current template file name equals its planned new one (case-insensitive): verification compares file names and would pass on an unchanged sheet. Resolve by renaming the new template files (for example a year or version suffix) and updating `template-map.md`. Note, not a flag: built-in title block on (the script switches it off). Per project, a new-template field that the sheets have no parameter for, and each rename in the map.
6. Regenerate `output/_queue.md` from every `output/<slug>/run-sheet.md`: table `project | sheets | sizes | flags | run sheet link`, flag-free projects first. It is rebuilt on every bulk run and never hand-edited.

## Outputs
- `plan.csv`, `run-sheet.md` -> `output/<slug>/`
- `_queue.md` -> `output/`

## Check
You read `_queue.md`, resolve the flags, and name the projects to swap (default: every flag-free one).
