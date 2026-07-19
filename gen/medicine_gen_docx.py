#!/usr/bin/env python3
"""Build Medicine.docx.json from the Word question bank in gen/Medicine.source.docx.

The Word file is a single 4-column table: #, Category, Question, Answer.
The Category column carries the difficulty:

    Easy       -> easy
    Difficult  -> hard
    anything else ("Fun", "…About the Human Body", …) -> medium

Reads the .docx as a zip and walks the table XML, so no python-docx needed.
"""
import json, os, re, zipfile
import xml.etree.ElementTree as ET
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC  = f"{BASE}/gen/Medicine.source.docx"
OUT  = f"{BASE}/gen/Medicine.docx.json"

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
TIER = {"easy": "easy", "difficult": "hard"}      # everything else falls to medium


def cell_text(tc):
    """A cell's paragraphs joined by newline, runs within a paragraph concatenated."""
    paras = ["".join(t.text or "" for t in p.iter(f"{W}t")) for p in tc.iter(f"{W}p")]
    return "\n".join(paras).strip()


def rows_from_docx(path):
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    tbl = next(root.iter(f"{W}tbl"))
    for tr in tbl.findall(f"{W}tr"):
        cells = [cell_text(tc) for tc in tr.findall(f"{W}tc")]
        if len(cells) == 4:
            yield cells


def main():
    rows = list(rows_from_docx(SRC))
    if rows and rows[0][1].strip().lower() == "category":
        rows = rows[1:]                            # drop the header row

    out, seen, skipped = [], set(), 0
    for _n, cat, q, a in rows:
        q = re.sub(r"\s+", " ", q).strip()
        a = re.sub(r"\s+", " ", a).strip()
        a = re.sub(r"\.$", "", a)                  # bank style keeps answers unpunctuated
        if not q or not a:
            skipped += 1; continue
        key = re.sub(r"[^a-z0-9]", "", q.lower())
        if key in seen:                            # the file repeats a few questions verbatim
            skipped += 1; continue
        seen.add(key)
        out.append({"q": q, "a": a,
                    "d": TIER.get(cat.strip().lower(), "medium"),
                    "src": "authored"})

    json.dump(out, open(OUT, "w"), ensure_ascii=False, indent=1)
    tiers = Counter(e["d"] for e in out)
    print(f"{len(rows)} rows -> {len(out)} questions ({skipped} skipped)")
    print(f"  easy {tiers['easy']} · medium {tiers['medium']} · hard {tiers['hard']}")
    print(f"  wrote {OUT}")


if __name__ == "__main__":
    main()
