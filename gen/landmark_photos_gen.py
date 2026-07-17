#!/usr/bin/env python3
"""Turn the user's own landmark photos into 'which country is this landmark in?'
questions. Reads photos from landmark-photos/, writes shrunk+optimized copies to
landmark-photos/opt/, and emits gen/LandmarkPhotos.authored.json.

Filename = COUNTRY, optionally followed by a difficulty word (easy/medium/hard).
Accepts the difficulty separated by a space or glued, and a trailing number for
multiple photos of one country:
  Egypt.jpeg            -> Egypt, medium
  australia hard.webp   -> Australia, hard
  ukhard.webp           -> United Kingdom, hard
  italy2.webp           -> Italy, medium
  "south africa hard.webp" -> South Africa, hard
"""
import json, os, re
from PIL import Image, ImageOps

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = f"{BASE}/landmark-photos"
OPT = f"{SRC}/opt"
OUT = f"{BASE}/gen/LandmarkPhotos.authored.json"
MAXDIM = 1100
os.makedirs(OPT, exist_ok=True)

ALIAS = {"usa":"United States", "us":"United States", "uk":"United Kingdom",
         "uae":"United Arab Emirates", "drc":"Democratic Republic of the Congo",
         "vatican":"Vatican City", "holland":"Netherlands"}
DIFFS = {"easy","medium","hard"}
EXTS = {".jpg",".jpeg",".png",".webp",".gif",".bmp",".heic",".tif",".tiff"}
SMALL = {"of","the","and"}

def title_country(s):
    s = re.sub(r"\s+", " ", s.strip())
    if s.lower() in ALIAS: return ALIAS[s.lower()]
    return " ".join(w if w in SMALL else w.capitalize() for w in s.split())

def slug(s): return re.sub(r"[^a-z0-9]+","-", s.lower()).strip("-")

out, skipped, used = [], [], {}
for fn in sorted(os.listdir(SRC)):
    path = os.path.join(SRC, fn)
    if not os.path.isfile(path): continue
    stem, ext = os.path.splitext(fn)
    if ext.lower() not in EXTS: continue

    s = stem.strip().lower()
    diff = "easy"                                          # default: no easy/medium/hard word -> easy
    m = re.search(r"[\s_]*(easy|medium|hard)\s*$", s)      # trailing difficulty (space or glued)
    if m:
        diff = m.group(1); s = s[:m.start()]
    s = re.sub(r"[\s_]*\d+\s*$", "", s).strip()            # drop trailing number (italy2 -> italy)
    country = title_country(s)
    if not country:
        skipped.append(f"{fn} (no country in name)"); continue

    key = slug(country)
    used[key] = used.get(key, 0) + 1
    outname = f"{key}.jpg" if used[key] == 1 else f"{key}-{used[key]}.jpg"
    try:
        im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
        im.thumbnail((MAXDIM, MAXDIM), Image.LANCZOS)      # shrink big images (never upscale)
        im.save(os.path.join(OPT, outname), "JPEG", quality=82, optimize=True)
    except Exception as e:
        skipped.append(f"{fn} (couldn't read: {e})"); continue
    out.append({"q":"Which country is this landmark in?", "a":country, "d":diff,
                "img":f"landmark-photos/opt/{outname}", "src":"authored"})

json.dump(out, open(OUT,"w"), ensure_ascii=False, indent=1)
from collections import Counter
c = Counter(e["d"] for e in out)
print(f"processed {len(out)} photos  (easy {c['easy']}, medium {c['medium']}, hard {c['hard']})")
for e in out:
    print(f"  [{e['d']:6}] {e['a']:22} <- {e['img']}")
for s in skipped:
    print("  SKIPPED:", s)
