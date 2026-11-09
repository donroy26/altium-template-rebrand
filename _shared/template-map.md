# Template map - the factory settings for every rebrand run

Filled once from [the questionnaire](../setup/questionnaire.md). Every value marked FILL is a placeholder: stage 02 stops and asks if one is still there.

## Template folder

FILL: folder holding the new `.SchDot` files, or "Workspace-managed" and the template names

## New template per sheet size

| Size (as the tool reports it) | New template file |
|---|---|
| A4 | FILL |
| A3 | FILL |
| A2 | FILL |
| A | FILL |
| B | FILL |
| C | FILL |

Add a row per new template. The size is the string `sch_inventory.py` reports for that template (for example `A3` or `custom 1100x850`); the setup step fills it by running the tool on each new template, not by hand. A sheet whose size has no row here is flagged by stage 02.

## Old-branding template files

FILL: file names of the old templates, one per line

## Parameter renames

| Old name | New name |
|---|---|
| (none, or FILL) | |

## Parameter action

FILL: default is "Add new parameters that exist in the template only"

## Projects and backup

- Project root folders: FILL
- Released or archived projects live in: FILL
- Backup method before each run: FILL
