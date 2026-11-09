#!/usr/bin/env python3
"""Read Altium SchDoc/SchDot files (no Altium needed) and write inventory.json and inventory.md.

    python _tools/sch_inventory.py <path to .PrjPcb, folder, .SchDoc or .SchDot> <out-dir>
    python _tools/sch_inventory.py --selftest

Record format: https://github.com/vadmium/python-altium/blob/master/format.md
Only dependency: olefile (imported when a file is read, so --selftest runs without it).
"""
import json
import ntpath
import os
import re
import struct
import sys

# SHEETSTYLE number -> size name, from format.md
SIZES = ["A4", "A3", "A2", "A1", "A0", "A", "B", "C", "D", "E", "Letter", "Legal", "Tabloid",
         "OrCAD A", "OrCAD B", "OrCAD C", "OrCAD D", "OrCAD E"]


def parse_records(data):
    """FileHeader bytes -> list of property dicts (upper-case keys). Framing per format.md:
    2-byte little-endian length, one zero byte, one type byte, then the payload.
    Only type 0 (property list) is kept."""
    recs, i = [], 0
    while i < len(data):
        if i + 4 > len(data):
            raise ValueError("truncated record header at byte %d" % i)
        n = struct.unpack_from("<H", data, i)[0]
        rtype = data[i + 3]
        payload = data[i + 4:i + 4 + n]
        if len(payload) < n:
            raise ValueError("truncated record at byte %d" % i)
        i += 4 + n
        if rtype != 0:
            continue
        props = {}
        for part in payload.rstrip(b"\x00").split(b"|"):
            key, eq, val = part.partition(b"=")
            if not eq:
                continue
            key = key.decode("cp1252", "replace").upper()
            # ponytail: %UTF8% values are decoded as UTF-8; everything else as cp1252
            props[key] = val.decode("utf-8" if key.startswith("%UTF8%") else "cp1252", "replace")
        recs.append(props)
    return recs


def get(rec, key):
    """Value of key, preferring the %UTF8% copy when the file carries one."""
    return rec.get("%UTF8%" + key, rec.get(key, ""))


def summarize(recs, sheet):
    out = {"sheet": sheet, "size": "", "custom_size": "", "template": "", "template_record": "",
           "has_template_record": False, "titleblock_on": False,
           "parameters": {}, "special_strings": []}
    strings = set()
    for r in recs:
        kind = r.get("RECORD", "")
        if kind == "31":
            style = r.get("SHEETSTYLE", "0")
            out["size"] = SIZES[int(style)] if style.isdigit() and int(style) < len(SIZES) else "style %s" % style
            if r.get("USECUSTOMSHEET") == "T":
                out["custom_size"] = "%sx%s" % (r.get("CUSTOMX", "?"), r.get("CUSTOMY", "?"))  # 1/100 inch
            out["template"] = r.get("TEMPLATEFILENAME", "")
            out["titleblock_on"] = r.get("TITLEBLOCKON") == "T"  # built-in title block
        elif kind == "39":
            out["has_template_record"] = True
            out["template_record"] = get(r, "FILENAME")
        elif kind == "41" and r.get("OWNERINDEX", "0") == "0":  # sheet-level, not a component's
            out["parameters"][get(r, "NAME")] = get(r, "TEXT")
        for key in ("TEXT", "%UTF8%TEXT"):
            if r.get(key, "").startswith("="):
                strings.add(r[key])
    out["template"] = out["template"] or out["template_record"]
    out["special_strings"] = sorted(strings)
    return out


def read_sheet(path, sheet):
    try:
        import olefile
        with olefile.OleFileIO(path) as ole:
            data = ole.openstream("FileHeader").read()
        return summarize(parse_records(data), sheet)
    except Exception as e:  # report the file, never skip it
        return {"sheet": sheet, "error": "%s: %s" % (type(e).__name__, e)}


def find_ci(base, rel):
    """Resolve rel under base ignoring case in every part (Windows path separators allowed)."""
    path = base
    for part in re.split(r"[\\/]", rel):
        if part in ("", "."):
            continue
        if part == "..":
            path = os.path.dirname(path)
            continue
        names = os.listdir(path) if os.path.isdir(path) else []
        hit = next((n for n in names if n.lower() == part.lower()), part)
        path = os.path.join(path, hit)
    return path


def sheet_list(target):
    """-> list of (full path, project-relative sheet name)."""
    if os.path.isdir(target):
        base = os.path.abspath(target)
        found = [os.path.join(d, f) for d, _, fs in os.walk(base) for f in fs if f.lower().endswith(".schdoc")]
    elif target.lower().endswith(".prjpcb"):
        base = os.path.dirname(os.path.abspath(target))
        with open(target, encoding="utf-8-sig", errors="replace") as fh:
            text = fh.read()
        rels = re.findall(r"^\s*DocumentPath\s*=\s*(.+?)\s*$", text, re.I | re.M)
        found = [find_ci(base, r) for r in rels if r.lower().endswith(".schdoc")]
    else:
        return [(target, os.path.basename(target))]
    return [(p, os.path.relpath(p, base).replace("\\", "/")) for p in sorted(found)]


def inventory(target):
    out = []
    for path, sheet in sheet_list(target):
        out.append(read_sheet(path, sheet) if os.path.isfile(path) else {"sheet": sheet, "error": "file not found"})
    return out


def table(rows):
    lines = ["| sheet | size | current template | parameter count | template record | built-in title block |",
             "|---|---|---|---|---|---|"]
    for r in rows:
        if "error" in r:
            lines.append("| %s | ERROR | %s | | | |" % (r["sheet"], r["error"]))
        else:
            size = r["size"] + (" (custom %s)" % r["custom_size"] if r["custom_size"] else "")
            lines.append("| %s | %s | %s | %d | %s | %s |" % (
                r["sheet"], size, r["template"] or "(none)", len(r["parameters"]),
                "yes" if r["has_template_record"] else "no", "on" if r["titleblock_on"] else "off"))
    return "\n".join(lines)


def run(target, out_dir):
    rows = inventory(target)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "source.txt"), "w", encoding="utf-8") as f:  # make_jobs.py reads this
        f.write(os.path.abspath(target) + "\n")
    with open(os.path.join(out_dir, "inventory.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
    with open(os.path.join(out_dir, "inventory.md"), "w", encoding="utf-8") as f:
        f.write("# Inventory\n\n" + table(rows) + "\n")
    return rows


def rec(text):
    """Build one framed record from text (selftest helper)."""
    body = text.encode("utf-8" if "%UTF8%" in text else "cp1252") + b"\x00"
    return struct.pack("<H", len(body)) + b"\x00\x00" + body


def selftest():
    data = b"".join([
        rec("|HEADER=Protel for Windows - Schematic Capture Binary File Version 5.0"),
        rec("|record=31|SHEETSTYLE=1|TITLEBLOCKON=T|USECUSTOMSHEET=T|CUSTOMX=1500|CUSTOMY=950|TEMPLATEFILENAME=C:\\t\\Old.SchDot"),
        rec("|RECORD=39|FILENAME=C:\\t\\Old.SchDot"),
        rec("|RECORD=41|NAME=Title|TEXT=Board"),
        rec("|RECORD=41|OWNERINDEX=5|NAME=Value|TEXT=10k"),
        rec("|RECORD=41|NAME=Rev|TEXT=A|%UTF8%TEXT=A\u00b5"),
        rec("|RECORD=4|TEXT==DocumentName"),
    ])
    r = summarize(parse_records(data), "a.SchDoc")
    assert r["size"] == "A3" and r["custom_size"] == "1500x950", r
    assert r["template"] == "C:\\t\\Old.SchDot" and r["template_record"] == "C:\\t\\Old.SchDot", r
    assert r["parameters"] == {"Title": "Board", "Rev": "A\u00b5"}, r["parameters"]  # component param skipped
    assert r["special_strings"] == ["=DocumentName"], r["special_strings"]
    assert r["titleblock_on"] and r["has_template_record"], r
    # template falls back to the RECORD=39 name; unknown style is reported, not guessed
    r = summarize(parse_records(rec("|RECORD=31|SHEETSTYLE=99") + rec("|RECORD=39|FILENAME=X.SchDot")), "b")
    assert r["size"] == "style 99" and r["template"] == "X.SchDot", r
    r = summarize(parse_records(rec("|RECORD=31|SHEETSTYLE=0")), "c")
    assert not r["has_template_record"] and not r["titleblock_on"] and r["size"] == "A4", r
    try:
        parse_records(data[:-3])
        raise SystemExit("truncated data was accepted")
    except ValueError:
        pass
    print("selftest ok")


def main():
    args = sys.argv[1:]
    if args == ["--selftest"]:
        return selftest()
    if len(args) != 2:
        sys.exit(__doc__)
    rows = run(*args)
    print(table(rows))
    if any("error" in r for r in rows):
        sys.exit(1)


if __name__ == "__main__":
    main()
