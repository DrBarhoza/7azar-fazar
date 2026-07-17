#!/usr/bin/env python3
"""Render country silhouettes (green SVG) from public-domain Natural Earth data
(johan/world.geo.json). Output: country-shapes/<slug>.svg"""
import json, math, os, re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = f"{BASE}/country-shapes"
os.makedirs(OUTDIR, exist_ok=True)
GREEN = "#37b34a"
SIZE = 420          # viewBox square
PAD = 14

feats = {f["properties"]["name"]: f for f in json.load(open(f"{BASE}/harvest/world.geo.json"))["features"]}

# display name -> dataset name (only where they differ)
ALIAS = {"United States": "United States of America", "Czech Republic": "Czech Republic",
         "Democratic Republic of the Congo": "Democratic Republic of the Congo"}

def polygons(feat):
    g = feat["geometry"]; t = g["type"]
    if t == "Polygon": return [g["coordinates"][0]]           # exterior rings only
    if t == "MultiPolygon": return [p[0] for p in g["coordinates"]]
    return []

def ring_area(r):
    s = 0.0
    for i in range(len(r) - 1):
        s += r[i][0]*r[i+1][1] - r[i+1][0]*r[i][1]
    return abs(s) / 2

def render(name):
    ds = ALIAS.get(name, name)
    if ds not in feats:
        return None, "no-data"
    rings = polygons(feats[ds])
    if not rings:
        return None, "no-rings"
    amax = max(ring_area(r) for r in rings)
    keep = [r for r in rings if ring_area(r) >= 0.03 * amax]   # drop tiny slivers/exclaves
    lats = [pt[1] for r in keep for pt in r]
    lat0 = math.radians(sum(lats)/len(lats))
    kx = math.cos(lat0) or 1e-3
    pts = [(pt[0]*kx, pt[1]) for r in keep for pt in r]
    minx = min(p[0] for p in pts); maxx = max(p[0] for p in pts)
    miny = min(p[1] for p in pts); maxy = max(p[1] for p in pts)
    w, h = maxx-minx or 1e-6, maxy-miny or 1e-6
    scale = (SIZE - 2*PAD) / max(w, h)
    ox = (SIZE - w*scale)/2; oy = (SIZE - h*scale)/2
    def tx(x, y):
        px = ox + (x*kx - minx)*scale
        py = SIZE - (oy + (y - miny)*scale)     # flip Y (north up)
        return f"{px:.1f},{py:.1f}"
    paths = []
    for r in keep:
        d = "M" + " L".join(tx(x, y) for x, y in r) + "Z"
        paths.append(d)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}">'
           f'<path d="{"".join(paths)}" fill="{GREEN}"/></svg>')
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    open(f"{OUTDIR}/{slug}.svg", "w").write(svg)
    return f"country-shapes/{slug}.svg", "ok"

# curated, recognizable, antimeridian-safe countries with difficulty
COUNTRIES = {
 "United Kingdom":"easy","United States":"easy","Italy":"easy","Australia":"easy",
 "Mexico":"easy","China":"easy","France":"easy","Japan":"easy","India":"easy",
 "Brazil":"easy","Canada":"easy","Egypt":"medium","Spain":"medium","Germany":"medium",
 "Chile":"medium","Argentina":"medium","South Africa":"medium","Norway":"medium",
 "Sweden":"medium","Portugal":"medium","Ireland":"medium","Iceland":"medium",
 "Greece":"medium","Turkey":"medium","Saudi Arabia":"medium","India ":"hard",
 "South Korea":"medium","Vietnam":"medium","Thailand":"hard","Cuba":"medium",
 "Madagascar":"medium","Sri Lanka":"hard","New Zealand":"medium","Netherlands":"hard",
 "Poland":"hard","Ukraine":"hard","Kenya":"hard","Nigeria":"hard","Morocco":"hard",
 "Iraq":"hard","Iran":"medium","Afghanistan":"hard","Nepal":"hard","Peru":"medium",
 "Colombia":"hard","Finland":"hard","Somalia":"hard","Pakistan":"hard","Indonesia":"hard",
}
results = {}
for name, diff in COUNTRIES.items():
    n = name.strip()
    path, status = render(n)
    results[n] = (path, status, diff)
ok = {n:v for n,v in results.items() if v[1]=="ok"}
bad = {n:v for n,v in results.items() if v[1]!="ok"}
print(f"rendered {len(ok)} shapes; failed {len(bad)}")
for n,(p,s,d) in bad.items(): print("  FAIL", n, s)
json.dump({n:{"path":v[0],"d":v[2]} for n,v in ok.items()},
          open(f"{BASE}/gen/shapes_index.json","w"), indent=1)
