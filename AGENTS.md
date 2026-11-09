# Altium Template Rebrand - entry and routing

This workspace re-brands the schematic sheet templates (title blocks) on your company's Altium Designer projects. Claude inventories each project, plans the swap, runs an Altium script that does the swap, and verifies the result from the files on disk. Doing the clicks by hand is the fallback if the script cannot be used.

## Where things live

| Folder | What it holds |
|---|---|
| `stages/` | the pipeline, in execution order; stages 01, 02 and 04 write to `output/<project-slug>/`, stage 03 writes one job list and log per batch |
| `_shared/` | factory: the template map, and the Altium steps and evidence |
| `_tools/` | Python tools, `altium/RebrandTemplates.pas` (the Altium script), `links.py` (checks every link) |
| `setup/` | one-time setup: prerequisites, pilot and the questionnaire |

## Route by what just happened

| If | Go to | Then stop at |
|---|---|---|
| asked to set up | [prerequisites](setup/prerequisites.md), then [questionnaire](setup/questionnaire.md) | answers written to [template-map](_shared/template-map.md) |
| asked to run the rebrand on one project | [01_inventory](stages/01_inventory/CONTEXT.md) | the stage's check |
| inventory passed its check | [02_plan](stages/02_plan/CONTEXT.md) | you name the projects to swap |
| asked to run the rebrand on every project under a folder | bulk runs in [CONTEXT](CONTEXT.md): stages 01 and 02 for each project | the queue: you approve the projects |
| you approved projects | [03_swap](stages/03_swap/CONTEXT.md), once for all approved projects | the log's last line |
| the swap log says no failures | [04_verify](stages/04_verify/CONTEXT.md), once per project | the stage's check |
| asked for status | scan `stages/*/output/` (one folder per project, plus the 03 log) and each `check.md` | report one line per project |

## The one rule

Nothing moves to the next stage until the last one's check passes.
