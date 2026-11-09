#!/usr/bin/env python3
"""Write the job list that _tools/altium/RebrandTemplates.pas reads.

    python _tools/make_jobs.py <templates folder> <slug> [<slug> ...]     (run from workspace root)
    python _tools/make_jobs.py --selftest

For each slug, joins stages/02_plan/output/<slug>/plan.csv with the project path in
stages/01_inventory/output/<slug>/source.txt. Writes stages/03_swap/output/jobs.txt, one line per sheet:
    project .PrjPcb path|sheet path|template path|titleblock_off      (absolute paths, grouped by project)
titleblock_off is 1 when the inventory shows the built-in title block on. Refuses if a template file is missing, or if a sheet's current template has the planned file name
(verification compares file names, so an in-place re-brand would pass on an unchanged sheet).
"""
import csv
import json
import ntpath
import os
import sys
import tempfile


def build(root, templates, slugs):
    """-> list of job lines. Raises SystemExit naming the first problem."""
    lines = []
    for slug in slugs:
        inv = os.path.join(root, "stages", "01_inventory", "output", slug)
        plan = os.path.join(root, "stages", "02_plan", "output", slug, "plan.csv")
        for p in (os.path.join(inv, "inventory.json"), os.path.join(inv, "source.txt"), plan):
            if not os.path.isfile(p):
                sys.exit("missing input for %s: %s" % (slug, p))
        with open(os.path.join(inv, "source.txt"), encoding="utf-8") as f:
            source = f.read().strip()
        with open(os.path.join(inv, "inventory.json"), encoding="utf-8") as f:
            before = {r["sheet"].lower(): r for r in json.load(f)}
        is_project = source.lower().endswith(".prjpcb")
        # sheet names are relative to the project file's folder, the scanned folder, or the single file's folder
        base = source if os.path.isdir(source) else os.path.dirname(source)
        with open(plan, encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                old = before.get(row["sheet"].lower())
                if old is None or "error" in old:
                    sys.exit("%s: sheet %s is not in the inventory or did not parse" % (slug, row["sheet"]))
                if ntpath.basename(old["template"].replace("/", "\\")).lower() == row["new_template"].lower():
                    sys.exit("%s: sheet %s already uses a template named %s; verification compares file names, "
                             "so rename the new template" % (slug, row["sheet"], row["new_template"]))
                tpl = os.path.join(templates, row["new_template"])
                if not os.path.isfile(tpl):
                    sys.exit("template file does not exist: %s" % tpl)
                lines.append("|".join([
                    source if is_project else "",
                    os.path.abspath(os.path.join(base, row["sheet"])),
                    os.path.abspath(tpl),
                    "1" if old["titleblock_on"] else "0"]))
    return lines


def selftest():
    root = tempfile.mkdtemp()
    tpl_dir = os.path.join(root, "tpl")
    os.makedirs(tpl_dir)
    open(os.path.join(tpl_dir, "New-A3.SchDot"), "w").close()
    inv = os.path.join(root, "stages", "01_inventory", "output", "p")
    os.makedirs(inv)
    os.makedirs(os.path.join(root, "stages", "02_plan", "output", "p"))
    proj = os.path.join(root, "proj", "P.PrjPcb")
    with open(os.path.join(inv, "source.txt"), "w") as f:
        f.write(proj + "\n")
    with open(os.path.join(inv, "inventory.json"), "w") as f:
        json.dump([{"sheet": "a.SchDoc", "titleblock_on": True, "template": "C:\\old\\Old.SchDot"},
                   {"sheet": "b.SchDoc", "titleblock_on": False, "template": ""}], f)
    with open(os.path.join(root, "stages", "02_plan", "output", "p", "plan.csv"), "w") as f:
        f.write("sheet,size,new_template\na.SchDoc,A3,New-A3.SchDot\nb.SchDoc,A3,New-A3.SchDot\n")
    lines = build(root, tpl_dir, ["p"])
    tpl = os.path.abspath(os.path.join(tpl_dir, "New-A3.SchDot"))
    a = os.path.abspath(os.path.join(root, "proj", "a.SchDoc"))
    b = os.path.abspath(os.path.join(root, "proj", "b.SchDoc"))
    assert lines == ["|".join([proj, a, tpl, "1"]), "|".join([proj, b, tpl, "0"])], lines
    try:
        build(root, os.path.join(root, "nowhere"), ["p"])
        raise AssertionError("missing template was accepted")
    except SystemExit as e:
        assert "template file does not exist" in str(e), e
    with open(os.path.join(inv, "inventory.json"), "w") as f:  # sheet a already uses a template named New-A3.SchDot
        json.dump([{"sheet": "a.SchDoc", "titleblock_on": True, "template": "D:\\x\\new-a3.schdot"},
                   {"sheet": "b.SchDoc", "titleblock_on": False, "template": ""}], f)
    try:
        build(root, tpl_dir, ["p"])
        raise AssertionError("same-name template was accepted")
    except SystemExit as e:
        assert "a.SchDoc" in str(e) and "New-A3.SchDot" in str(e), e
    print("selftest ok")


def main():
    args = sys.argv[1:]
    if args == ["--selftest"]:
        return selftest()
    if len(args) < 2:
        sys.exit(__doc__)
    lines = build(".", args[0], args[1:])
    out = os.path.join("stages", "03_swap", "output")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "jobs.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote %d jobs to %s" % (len(lines), os.path.join(out, "jobs.txt")))


if __name__ == "__main__":
    main()
