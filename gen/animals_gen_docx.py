#!/usr/bin/env python3
"""Build Animals.docx.json from the Word question bank in gen/Animals.source.docx.

One 5-column table: No., Category, Difficulty, Question, Answer. Unlike the
medicine bank the difficulty has its own column (Easy / Medium / Hard) — the
Category column is the animal group (Mammals, Birds, …) and is not used, since
these all land in the one Animals topic.

These questions are ADDED to Animals alongside the existing harvested and
authored sets, so assemble.py dedupes them against those.
"""
import json, os, re
from collections import Counter

from docx_table import rows_from_docx

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC  = f"{BASE}/gen/Animals.source.docx"
OUT  = f"{BASE}/gen/Animals.docx.json"

TIER = {"easy": "easy", "medium": "medium", "hard": "hard"}


def main():
    rows = list(rows_from_docx(SRC, width=5))
    if rows and rows[0][3].strip().lower() == "question":
        rows = rows[1:]                            # drop the header row

    out, seen, skipped = [], set(), 0
    for _n, _cat, diff, q, a in rows:
        q = re.sub(r"\s+", " ", q).strip()
        a = re.sub(r"\s+", " ", a).strip()
        if not q or not a:
            skipped += 1; continue
        key = re.sub(r"[^a-z0-9]", "", q.lower())
        if key in seen:
            skipped += 1; continue
        seen.add(key)
        # answers keep their "!" and any "(Also accepted: …)" note — that aside is
        # what the host needs to judge a near-miss answer out loud
        out.append({"q": q, "a": a,
                    "d": TIER.get(diff.strip().lower(), "medium"),
                    "src": "authored"})

    json.dump(out, open(OUT, "w"), ensure_ascii=False, indent=1)
    tiers = Counter(e["d"] for e in out)
    print(f"{len(rows)} rows -> {len(out)} questions ({skipped} skipped)")
    print(f"  easy {tiers['easy']} · medium {tiers['medium']} · hard {tiers['hard']}")
    print(f"  wrote {OUT}")


if __name__ == "__main__":
    main()
