#!/usr/bin/env python3
"""Author two picture/ranking country formats:
  - Country Shapes: "Which country has this shape?" (+img silhouette)
  - Rank Countries: order 4 countries by area or by population
Outputs: gen/CountryShapes.authored.json , gen/RankCountries.authored.json"""
import json, os, random, itertools
random.seed(7)
BASE = "/Users/el-professor/Downloads/7azar-fazar"

# ---------- shape questions ----------
shapes = json.load(open(f"{BASE}/gen/shapes_index.json"))
shape_q = []
for country, info in shapes.items():
    shape_q.append({"q": "Which country has this shape?", "a": country,
                    "img": info["path"], "d": info["d"], "src": "authored"})
json.dump(shape_q, open(f"{BASE}/gen/CountryShapes.authored.json", "w"), ensure_ascii=False, indent=1)

# ---------- ranking questions ----------
# country: (area_1000km2, population_millions, famous?)
DATA = {
 "Russia":(17098,144,1),"Canada":(9985,39,1),"United States":(9834,340,1),"China":(9597,1425,1),
 "Brazil":(8516,216,1),"Australia":(7692,26,1),"India":(3287,1441,1),"Argentina":(2780,46,1),
 "Kazakhstan":(2725,20,0),"Algeria":(2382,45,0),"Saudi Arabia":(2150,37,1),"Mexico":(1964,129,1),
 "Indonesia":(1905,279,1),"Sudan":(1861,48,0),"Libya":(1760,7,0),"Iran":(1648,89,1),
 "Mongolia":(1564,3.4,0),"Peru":(1285,34,1),"Chad":(1284,18,0),"Niger":(1267,26,0),
 "Angola":(1247,36,0),"Mali":(1240,22,0),"South Africa":(1221,60,1),"Colombia":(1142,52,1),
 "Ethiopia":(1104,127,0),"Bolivia":(1099,12,0),"Egypt":(1002,113,1),"Nigeria":(924,229,1),
 "Tanzania":(947,67,0),"Venezuela":(916,28,1),"Pakistan":(881,245,1),"Turkey":(784,85,1),
 "Chile":(756,19,1),"Zambia":(753,20,0),"Myanmar":(677,54,0),"Afghanistan":(653,42,0),
 "France":(552,65,1),"Thailand":(513,72,1),"Spain":(506,48,1),"Sweden":(450,10,1),
 "Germany":(358,84,1),"Japan":(378,123,1),"Norway":(385,5.5,1),"Italy":(301,59,1),
 "Vietnam":(331,99,1),"Poland":(313,38,1),"United Kingdom":(244,68,1),"Greece":(132,10,1),
 "Portugal":(92,10,1),"Ireland":(70,5.1,1),"Iceland":(103,0.37,1),"Cuba":(110,11,1),
 "South Korea":(100,52,1),"Nepal":(147,30,0),"Kenya":(580,55,1),"Morocco":(447,37,1),
 "Netherlands":(42,18,1),"New Zealand":(268,5.2,1),"Philippines":(300,118,1),"Ukraine":(604,37,1),
}

def make_rank(metric, idx, label, direction="largest"):
    countries = list(DATA)
    out, seen = [], set()
    tries = 0
    while len(out) < 240 and tries < 60000:
        tries += 1
        four = random.sample(countries, 4)
        key = frozenset(four)
        if key in seen:
            continue
        vals = sorted(four, key=lambda c: DATA[c][idx], reverse=True)
        v = [DATA[c][idx] for c in vals]
        # need clearly separated values (no near-ties) for an unambiguous answer
        if any(v[i] < v[i+1] * 1.18 for i in range(3)):
            continue
        seen.add(key)
        fame = sum(DATA[c][2] for c in four)
        sep = min(v[i] / v[i+1] for i in range(3))
        d = "easy" if (fame == 4 and sep >= 2.2) else ("medium" if sep >= 1.6 else "hard")
        shown = four[:]; random.shuffle(shown)
        q = (f"Put these four countries in order by {label}, from {direction} to "
             f"{'smallest' if direction=='largest' else 'largest'}: " + ", ".join(shown))
        out.append({"q": q, "a": ", ".join(vals), "d": d, "src": "authored"})
    return out

area = make_rank("area", 0, "AREA (land size)", "largest")
pop  = make_rank("pop", 1, "POPULATION", "largest")
# balance: cap each metric to a sensible total, blend
rank = area[:120] + pop[:120]
from collections import Counter
json.dump(rank, open(f"{BASE}/gen/RankCountries.authored.json", "w"), ensure_ascii=False, indent=1)

sc = Counter(x["d"] for x in shape_q); rc = Counter(x["d"] for x in rank)
print(f"Country Shapes: {len(shape_q)} (easy={sc['easy']} medium={sc['medium']} hard={sc['hard']})")
print(f"Rank Countries: {len(rank)} (easy={rc['easy']} medium={rc['medium']} hard={rc['hard']}) "
      f"[area={len(area)} pop={len(pop)} available]")
