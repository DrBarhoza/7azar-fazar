#!/usr/bin/env python3
"""El-Barahma family photo round. Reads barahma-photos/answers.txt + the photos,
shrinks/optimizes each into barahma-photos/opt/, and writes gen/Barahma.authored.json.
Each entry is a blur-reveal question with separate where/when answers."""
import json, os, re, subprocess
from PIL import Image, ImageOps

def load_image(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in (".heic", ".heif"):                 # PIL can't read HEIC — convert via macOS sips
        tmp = path + ".__conv.jpg"
        subprocess.run(["sips","-s","format","jpeg",path,"--out",tmp], check=True, capture_output=True)
        im = Image.open(tmp); im.load(); os.remove(tmp); return im
    return Image.open(path)

BASE = "/Users/el-professor/Downloads/7azar-fazar"
SRC = f"{BASE}/barahma-photos"
OPT = f"{SRC}/opt"
ANS = f"{SRC}/answers.txt"
OUT = f"{BASE}/gen/Barahma.authored.json"
os.makedirs(OPT, exist_ok=True)
DIFFS = {"easy","medium","hard"}

def slug(s): return re.sub(r"[^a-z0-9]+","-", s.lower()).strip("-")

FLAT = "hard"   # no per-photo difficulty; every El-Barahma photo is one flat value (30 pts)
out, missing, used = [], [], {}
for raw in open(ANS, encoding="utf-8"):
    line = raw.strip()
    if not line or line.startswith("#"): continue
    line = re.sub(r"\s+#.*$", "", line)          # strip trailing review comments
    parts = [p.strip() for p in line.split("|")]
    if len(parts) < 4:
        missing.append(f"(bad line, need filename|who|where|when) -> {line}"); continue
    fn, who, where, when = parts[0], parts[1], parts[2], parts[3]
    path = os.path.join(SRC, fn)
    if not os.path.isfile(path):
        missing.append(f"{fn} (file not found)"); continue
    key = slug(os.path.splitext(fn)[0])
    used[key] = used.get(key,0) + 1
    outname = f"{key}.jpg" if used[key] == 1 else f"{key}-{used[key]}.jpg"
    try:
        im = ImageOps.exif_transpose(load_image(path)).convert("RGB")
        im.thumbnail((1100,1100), Image.LANCZOS)
        im.save(os.path.join(OPT, outname), "JPEG", quality=82, optimize=True)
    except Exception as e:
        missing.append(f"{fn} (couldn't read: {e})"); continue
    ref = f"B{len(out)+1}"                    # stable id so the host can look it up
    out.append({"q":"Who is in this photo, and where and when was it taken?",
                "a":f"{who} · {where} · {when}",
                "who":who, "where":where, "when":when, "d":FLAT, "type":"barahma",
                "t":120,                      # photo round always gets 2 minutes
                "ref":ref,
                "img":f"barahma-photos/opt/{outname}", "src":"authored"})

json.dump(out, open(OUT,"w"), ensure_ascii=False, indent=1)

# ---- private HOST SHEET: self-contained HTML (photos embedded) for the host's phone ----
import base64, io
cards = []
for e in out:
    p = os.path.join(BASE, e["img"])
    im = Image.open(p); im.thumbnail((240, 240), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=70)
    b64 = base64.b64encode(buf.getvalue()).decode()
    cards.append(
      f'<div class="row"><span class="ref">{e["ref"]}</span>'
      f'<img src="data:image/jpeg;base64,{b64}">'
      f'<div class="ans"><b>Who:</b> {e["who"]}<br><b>Where:</b> {e["where"]}<br><b>When:</b> {e["when"]}</div></div>')
html = ("<!doctype html><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>El-Barahma — Host Sheet</title><style>"
        "body{font-family:-apple-system,sans-serif;background:#fff;color:#111;margin:0;padding:12px}"
        "h1{font-size:17px;margin:4px 0 2px}p.warn{color:#c00;font-size:13px;margin:0 0 10px}"
        ".row{display:flex;gap:10px;align-items:center;border-bottom:1px solid #e3e3e3;padding:9px 0}"
        ".ref{font-weight:800;color:#c00;min-width:34px;font-size:15px}"
        "img{width:104px;border-radius:6px;flex:0 0 auto}.ans{font-size:13px;line-height:1.45}"
        "</style><h1>El-Barahma — Host Sheet</h1>"
        "<p class='warn'>Keep this on your phone — do not mirror to the TV.</p>" + "".join(cards))
open(f"{BASE}/barahma-host-sheet.html", "w", encoding="utf-8").write(html)
print(f"host sheet -> barahma-host-sheet.html ({len(html)//1024} KB, open it on your phone)")
from collections import Counter
c = Counter(e["d"] for e in out)
print(f"El-Barahma: {len(out)} photos (easy {c['easy']}, medium {c['medium']}, hard {c['hard']})")
for e in out:
    print(f"  {e['who']} / {e['where']} / {e['when']}  <- {e['img']}")
for m in missing: print("  SKIPPED:", m)
if not out: print("  (no photos yet — add lines to answers.txt and drop the photos in)")
