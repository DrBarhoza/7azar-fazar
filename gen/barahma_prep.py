#!/usr/bin/env python3
"""Append NEW barahma photos to barahma-photos/answers.txt by parsing filenames.
Existing lines (and any manual fixes) are preserved."""
import os, re
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = f"{BASE}/barahma-photos"
ANS = f"{SRC}/answers.txt"
EXTS = {".jpg",".jpeg",".png",".webp",".heic",".heif",".tif",".tiff"}

PLACE = {"saudiarabia":"Saudi Arabia","usa":"USA","foukabay":"Fouka Bay","maadi":"Maadi",
 "marina":"Marina","giza":"Giza","qatar":"Qatar","dubai":"Dubai","jordan":"Jordan",
 "italy":"Italy","egypt":"Egypt","london":"London","worldwide":"worldwide",
 "northcoast":"North Coast","raselbar":"Ras El-Bar","cairo":"Cairo","sharmelsheikh":"Sharm El-Sheikh"}
def place(s):
    s = s.strip()
    if not s: return "?"
    key = s.lower().replace(" ","")
    if key in PLACE: return PLACE[key]
    return " ".join(PLACE.get(w.lower(), w.upper() if len(w)<=3 else w.capitalize()) for w in s.split())
def names(tok):
    return ", ".join(n.strip().capitalize() for n in tok.split(",") if n.strip())

def parse(fn):
    base = os.path.splitext(fn)[0].strip()
    yrs = re.findall(r"(?:19|20)\d{2}", base)
    when = yrs[-1] if yrs else "?"
    body = base[:base.rfind(when)].strip() if yrs else base
    toks = body.split()
    low = body.lower()
    if low.startswith("all family except") and len(toks) >= 4:
        who = "All family except " + toks[3].capitalize(); wt = toks[4:]
    elif low.startswith("all family"):
        who = "All family"; wt = toks[2:]
    elif toks:
        who = names(toks[0]); wt = toks[1:]
    else:
        who = "?"; wt = []
    wt = [w for w in wt if w.lower() != "corona"]
    if "corona" in low: when += " (Covid)"
    where = place(" ".join(wt)) if wt else "?"
    return who, where, when

# existing content + listed filenames
existing = open(ANS, encoding="utf-8").read() if os.path.exists(ANS) else ""
listed = set()
for ln in existing.splitlines():
    ln = ln.strip()
    if ln and not ln.startswith("#"):
        listed.add(ln.split("|")[0].strip().lower())

added = []
for fn in sorted(os.listdir(SRC)):
    if fn.startswith(".") or fn in ("opt","answers.txt"): continue
    if os.path.splitext(fn)[1].lower() not in EXTS: continue
    if fn.lower() in listed: continue
    who, where, when = parse(fn)
    note = "   # ← review" if (where == "?" or who == "?") else ""
    added.append((fn, who, where, when, note))

if added:
    with open(ANS, "a", encoding="utf-8") as f:
        if not existing.endswith("\n"): f.write("\n")
        for fn,who,where,when,note in added:
            f.write(f"{fn} | {who} | {where} | {when}{note}\n")

print(f"appended {len(added)} new line(s):")
for fn,who,where,when,note in added:
    print(f"  {who}  |  {where}  |  {when}{'   <-- REVIEW' if note else ''}")
