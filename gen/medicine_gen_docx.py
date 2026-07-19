#!/usr/bin/env python3
"""Build Medicine.docx.json from the Word question bank in gen/Medicine.source.docx.

The Word file is a single 4-column table: #, Category, Question, Answer.
The Category column carries the difficulty:

    Easy       -> easy
    Difficult  -> hard
    anything else ("Fun", "…About the Human Body", …) -> medium

Reads the .docx as a zip and walks the table XML, so no python-docx needed.
"""
import json, os, re
from collections import Counter

from docx_table import rows_from_docx

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC  = f"{BASE}/gen/Medicine.source.docx"
OUT  = f"{BASE}/gen/Medicine.docx.json"

TIER = {"easy": "easy", "difficult": "hard"}      # everything else falls to medium


def main():
    rows = list(rows_from_docx(SRC, width=4))
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
