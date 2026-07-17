#!/usr/bin/env python3
"""Assemble verified + authored questions into one OPEN-ENDED loadable file.
- strips embedded (A)(B)(C)(D) options and the answer-letter prefix
- drops 'which of the following' questions that need options to make sense
- tags every question  "src": "verified" | "authored"
- caps each tier at 300
"""
import json, re, os
from collections import Counter

BASE = "/Users/el-professor/Downloads/7azar-fazar"
H, G = f"{BASE}/harvest", f"{BASE}/gen"
OUT = f"{BASE}/trivia-questions.json"
CAP = 300

SRC = {
 "Geography":      ("Geography.json",      ["Geography.easy.json"]),
 "History":        ("History.json",        []),
 "Hollywood":      ("Hollywood.json",      []),
 "Animals":        ("Animals.clean.json",  ["Animals.authored.json"]),
 "Medicine":       ("Medicine.clean.json", ["Medicine.authored.json"]),
 "Soccer":         ("Soccer.clean.json",   []),
 "Countries":      (None, ["Emoji.authored.json", "EmojiPdf.authored.json", "Capitals.authored.json",
                           "CountryShapes.authored.json", "RankCountries.authored.json",
                           "LandmarkPhotos.authored.json"]),
 "El-Barahma":     (None, ["Barahma.authored.json"]),
}

NEEDS_OPTIONS = re.compile(r"which of (these|the following)|of the following|"
                           r"which one of the|which of the two", re.I)

def load(path, topic):
    d = json.load(open(path))
    return d[topic] if isinstance(d, dict) else d

def to_open(e):
    q = re.split(r"\s+\(A\)", e["q"])[0].strip()
    a = re.sub(r"^[A-E]\)\s*", "", str(e["a"])).strip()
    return q, a

def stem(q):
    return re.sub(r"[^a-z0-9]", "", q.lower())

bank, report = {}, []
for topic, (vf, gens) in SRC.items():
    rows = []
    if vf:
        for e in load(f"{H}/{vf}", topic):
            e["src"] = "verified"; rows.append(e)
    for gf in gens:
        for e in load(f"{G}/{gf}", topic):
            e["src"] = "authored"; rows.append(e)

    seen, tiers = set(), {"easy": [], "medium": [], "hard": []}
    dropped = 0
    for e in rows:
        q, a = to_open(e)
        if NEEDS_OPTIONS.search(q) or len(q) < 8 or not a:
            dropped += 1; continue
        # emoji puzzles share wording ("Which country?"); the glyphs live in the
        # non-ascii part, so key emoji questions on their raw text, not the stem
        has_emoji = any(ord(ch) > 0x2000 for ch in q)
        k = stem(q) + "|" + (e["img"] if e.get("img") else (q if has_emoji else stem(a)))
        if k in seen:
            continue
        d = e["d"] if e["d"] in tiers else "medium"
        if len(tiers[d]) >= CAP:
            continue
        seen.add(k)
        entry = {"q": q, "a": a, "d": d, "src": e["src"]}
        if e.get("img"): entry["img"] = e["img"]
        if e.get("t"):   entry["t"] = e["t"]
        if e.get("type") == "barahma":          # El-Barahma photo round: keep who/where/when
            entry["type"] = "barahma"
            for f in ("who","where","when","ref"):
                if e.get(f): entry[f] = e[f]
        tiers[d].append(entry)
    entries = tiers["easy"] + tiers["medium"] + tiers["hard"]
    if not entries:
        continue                     # skip empty topics (e.g. El-Barahma before photos added)
    bank[topic] = entries
    vc = sum(1 for e in entries if e["src"] == "verified")
    ac = sum(1 for e in entries if e["src"] == "authored")
    report.append((topic, len(entries),
                   (len(tiers["easy"]), len(tiers["medium"]), len(tiers["hard"])),
                   vc, ac, dropped))

json.dump(bank, open(OUT, "w"), ensure_ascii=False, indent=1)
print(f"{'topic':<11}{'total':>6}  {'e/m/h':>15}   verified  authored  (dropped)")
grand = 0
for topic, tot, tiers, vc, ac, dr in report:
    grand += tot
    print(f"{topic:<11}{tot:>6}  {str(tiers):>15}   {vc:>8}  {ac:>8}  ({dr})")
print(f"{'TOTAL':<11}{grand:>6}")
