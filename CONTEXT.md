# Altium Template Rebrand - the pipeline

The flow in one line: read every sheet, plan the template per size, an Altium script swaps them, read every sheet again from disk and compare.

| Stage | Job |
|---|---|
| `01_inventory` | read sheets, record size and template |
| `02_plan` | choose templates, flag problems |
| `03_swap` | build job list, run Altium script |
| `04_verify` | re-read and compare to plan |

Each stage's own `CONTEXT.md` holds its inputs, outputs and check.

Factory (stable, every run): `_shared/{template-map.md, altium-steps.md}`
Product (new each run): `stages/NN_x/output/`

## Project slug and path

The slug is the project file name without extension, in kebab-case (`Main Board.PrjPcb` becomes `main-board`). If two projects would share a slug, prefix the parent folder name, also kebab-case (`rev-b-main-board`).

All stages must run on the same project path. If you work on a copy, inventory, swap and verify all point at the copy.

## Bulk runs

Given a root folder, find every `.PrjPcb` under it. Run stage 01 and stage 02 for each project. Stage 02 also regenerates `stages/02_plan/output/_queue.md`. You read the queue, resolve the flags and name the projects to swap. Run stage 03 once for all of them, then stage 04 for each project. A single-project run is the same stages for one project.

## Status

Status is whatever exists, read by scanning `stages/*/output/`: a project is through a stage when its folder there holds the stage's artifacts and any `check.md` says pass. Stage 03 is through when `stages/03_swap/output/swap-log.txt` ends with `DONE <n> ok, 0 failed`. A placeholder that only keeps the empty folder in git does not count, and `_queue.md` is an index, not a result.
