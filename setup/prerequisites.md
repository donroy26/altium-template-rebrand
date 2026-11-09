# Prerequisites - what you need before the first run

Do these in order. Each one is a one-time job except the backup, which repeats per run.

1. Claude Code, either the desktop app's Code tab or the CLI, opened on this folder with access to your project folders. Plain chat Claude cannot read the files.
2. Python 3.9 or later, then `pip install olefile`. The commands in these files say `python`; on Windows the launcher may be `py` instead.
3. The new `.SchDot` templates, finished, one per standard sheet size, in one folder. In Altium, point Preferences > Data Management > Templates at that folder so the templates show in the Sheet Templates menu. The new files need names different from the old templates' names, because the script and stage 04 prove the swap by comparing file names, and a same-named file would look done before anything changed.
4. Projects in version control, or copied before each run. For Altium 365 Workspace projects, the swap is an ordinary edit that needs a commit afterwards.
5. The pilot. The Altium script has never been run, so it is untested until you pass this. Only after a pass is the workflow used on real projects. On a scratch COPY of one project:
   1. Run stages 01 and 02 on the copy, and approve it.
   2. Make the job list: "Run stage 03 for the pilot", which runs `_tools/make_jobs.py`.
   3. Edit `WorkspaceRoot` at the top of `_tools/altium/RebrandTemplates.pas` to this folder, ending in a backslash.
   4. In Altium, File > Run Script, browse to the file and run `RunProbe`. If the procedures do not list, add the file to a script project and run it from there.
   5. Ask Claude to read `stages/03_swap/output/swap-log.txt`. It tells you which method worked; set `Method` to that number.
   6. If Altium reports a script error, paste the error into Claude Code on your machine. That is where the script gets fixed.
   7. Run `RunBatch`, then stage 04. Fill the probe answer and the unconfirmed list in [altium-steps](../_shared/altium-steps.md).
6. The prompts to use:
   - "Read AGENTS.md and set me up", once.
   - "Run the rebrand on <path to .PrjPcb>", per project.
   - "Run the rebrand on every project under <folder>", for a bulk run.
   - "status", for where every project stands.

Test status: the inventory tool (`sch_inventory.py`) was run on 85 real `.SchDoc` files and 2 `.SchDot` files from four public hardware repositories on GitHub (last commits 2018, 2025 and 2026), with sheets that use a sheet template and sheets that do not. All parsed, and the sheet counts matched the `.PrjPcb` document lists. `make_jobs.py` and `verify.py` were run once each on one of those projects in a scratch copy of this workspace, without any swap: `make_jobs.py` wrote the job list and refused a new template whose file name equals the current one, and `verify.py` reported the expected template mismatch. Never run: the Altium script `RebrandTemplates.pas`, and anything that needs Altium. That includes the swap itself, so the passing path of `verify.py` has not been seen on a really swapped project, and `make_jobs.py` and `verify.py` have not seen a project from your company. Check the first inventory against the Projects panel in Altium before you trust it. If the script cannot be made to work, the manual steps in [altium-steps](../_shared/altium-steps.md) still do the swap.
