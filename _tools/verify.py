#!/usr/bin/env python3
"""Compare a project after the Altium swap against the inventory and plan.

    python _tools/verify.py <path to .PrjPcb or folder> <project-slug>     (run from workspace root)
    python _tools/verify.py --selftest

Reads  stages/01_inventory/output/<slug>/inventory.json and stages/02_plan/output/<slug>/plan.csv
Writes stages/04_verify/output/<slug>/{inventory.json,inventory.md,check.md}; exit 0 on pass, 1 on fail.
"""
import csv
import json
import ntpath
import os
import sys

import sch_inventory


def base(name):
    return ntpath.basename(name.replace("/", "\\")).lower()


def compare(before, after, plan):
    """-> (list of problems, list of per-sheet detail lines). Empty problems means pass."""
    problems, notes = [], []
    now = {r["sheet"].lower(): r for r in after}
    planned = {p["sheet"].lower(): p for p in plan}
    for r in after:
        if "error" in r:
            problems.append("%s failed to parse (%s)" % (r["sheet"], r["error"]))
    for key, p in planned.items():
        r = now.get(key)
        if r is None:
            problems.append("%s is missing" % p["sheet"])
        elif "error" not in r and base(r["template"]) != base(p["new_template"]):
            problems.append("%s has template %s, planned %s" % (r["sheet"], base(r["template"]) or "(none)", p["new_template"]))
    for b in before:
        r = now.get(b["sheet"].lower())
        if "error" in b:
            continue
        if r is None:
            problems.append("%s existed before and is missing" % b["sheet"])
        elif "error" not in r:
            for name, text in b["parameters"].items():
                if name not in r["parameters"]:
                    problems.append("%s: parameter %s is gone" % (b["sheet"], name))
                elif r["parameters"][name] != text:
                    problems.append("%s: parameter %s changed from %r to %r" % (b["sheet"], name, text, r["parameters"][name]))
    for r in after:
        if "error" in r:
            notes.append("- %s: error" % r["sheet"])
        else:
            notes.append("- %s: %s, template %s, %d parameters%s" % (
                r["sheet"], r["size"], base(r["template"]) or "(none)", len(r["parameters"]),
                "" if r["sheet"].lower() in planned else " (not in plan)"))
    return problems, notes


def load(path):
    if not os.path.isfile(path):
        sys.exit("missing input: %s (run the earlier stage first)" % path)
    return path


def main():
    args = sys.argv[1:]
    if args == ["--selftest"]:
        return selftest()
    if len(args) != 2:
        sys.exit(__doc__)
    target, slug = args
    with open(load("stages/01_inventory/output/%s/inventory.json" % slug), encoding="utf-8") as f:
        before = json.load(f)
    with open(load("stages/02_plan/output/%s/plan.csv" % slug), encoding="utf-8-sig", newline="") as f:
        plan = list(csv.DictReader(f))
    out_dir = "stages/04_verify/output/%s" % slug
    after = sch_inventory.run(target, out_dir)
    problems, notes = compare(before, after, plan)
    more = " (+%d more)" % (len(problems) - 3) if len(problems) > 3 else ""
    first = "fail: " + "; ".join(problems[:3]) + more if problems else "pass"
    body = ["Problems:"] + ["- " + p for p in problems] + [""] if problems else []
    with open(os.path.join(out_dir, "check.md"), "w", encoding="utf-8") as f:
        f.write("\n".join([first, ""] + body + ["Sheets:"] + notes) + "\n")
    print(first)
    sys.exit(1 if problems else 0)


def selftest():
    def sheet(name, template, **params):
        return {"sheet": name, "size": "A3", "template": template, "parameters": dict(params)}
    before = [sheet("a.SchDoc", "C:\\old\\Old.SchDot", Title="Board", Rev="A")]
    plan = [{"sheet": "a.SchDoc", "size": "A3", "new_template": "New-A3.SchDot"}]
    good = [sheet("A.schdoc", "D:\\x\\new-a3.schdot", Title="Board", Rev="A", Extra="x")]
    assert compare(before, good, plan)[0] == []
    bad = [sheet("a.SchDoc", "C:\\old\\Old.SchDot", Title="Board", Rev="A")]
    p = compare(before, bad, plan)[0]
    assert len(p) == 1 and "planned New-A3.SchDot" in p[0], p
    changed = [sheet("a.SchDoc", "New-A3.SchDot", Title="Other")]
    p = compare(before, changed, plan)[0]
    assert len(p) == 2 and any("parameter Title changed" in x for x in p) and any("parameter Rev is gone" in x for x in p), p
    assert compare(before, [], plan)[0] != []
    assert compare(before, [{"sheet": "a.SchDoc", "error": "boom"}], plan)[0] != []
    print("selftest ok")


if __name__ == "__main__":
    main()
