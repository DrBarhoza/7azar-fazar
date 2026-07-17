#!/usr/bin/env python3
"""Harvest verified trivia questions from OpenTDB + The Trivia API into the
game's topic-JSON format. Multiple-choice, options embedded in the question.

Usage:  python3 harvest.py <topic> [<topic> ...]
Writes  harvest/<topic>.json  (incrementally) and prints per-difficulty counts.
"""
import sys, os, re, json, time, html, random, urllib.request, urllib.parse

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = f"{BASE}/harvest"
CAP = 300                     # per difficulty per topic
DIFFS = ("easy", "medium", "hard")

# topic -> {"tapi": trivia-api category or {"tags":..}, "otdb": [opentdb cat ids]}
TOPICS = {
    "Geography": {"tapi_cat": "geography",   "otdb": [22]},
    "History":   {"tapi_cat": "history",     "otdb": [23]},
    "Hollywood": {"tapi_cat": "film_and_tv", "otdb": [11, 14]},
    "Animals":   {"tapi_tags": "animals",    "otdb": [27]},
    "Medicine":  {"tapi_tags": "medicine,human_body,anatomy,health,biology",
                  "otdb": [17]},
    "Soccer":    {"tapi_tags": "football,soccer", "tapi_cat": "sport_and_leisure",
                  "otdb": [21]},
}

def get(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=25) as r:
                return json.load(r)
        except Exception as e:
            time.sleep(2 + 3 * i)
    return None

def clean(s):
    return html.unescape(s or "").replace("’", "'").strip()

def norm(q):
    return re.sub(r"[^a-z0-9]", "", q.lower())

def make_entry(text, correct, incorrect, diff):
    text, correct = clean(text), clean(correct)
    opts = [correct] + [clean(x) for x in incorrect]
    opts = [o for o in opts if o]
    if len(opts) < 3 or len(text) < 8 or len(text) > 300:
        return None
    if any(len(o) > 70 for o in opts):
        return None
    if re.search(r"following|which of these|image|shown below", text, re.I) and len(opts) < 4:
        return None
    random.shuffle(opts)
    ci = opts.index(correct)
    q = text + "  " + "  ".join(f"({chr(65+i)}) {o}" for i, o in enumerate(opts))
    return {"q": q, "a": f"{chr(65+ci)}) {correct}", "d": diff}

# ---------- The Trivia API ----------
def harvest_tapi(cfg, diff, seen, bucket):
    base = "https://the-trivia-api.com/v2/questions?limit=50&difficulties=" + diff
    if cfg.get("tapi_cat"):
        base += "&categories=" + cfg["tapi_cat"]
    if cfg.get("tapi_tags"):
        base += "&tags=" + urllib.parse.quote(cfg["tapi_tags"])
    stalls = 0
    while len(bucket) < CAP and stalls < 12:
        data = get(base)
        if not data:
            stalls += 1; time.sleep(1); continue
        new = 0
        for item in data:
            text = item.get("question", {}).get("text", "")
            k = norm(text)
            if not k or k in seen:
                continue
            e = make_entry(text, item.get("correctAnswer"),
                           item.get("incorrectAnswers", []), diff)
            if e:
                seen.add(k); bucket.append(e); new += 1
                if len(bucket) >= CAP:
                    break
        stalls = stalls + 1 if new < 3 else 0
        time.sleep(0.6)

# ---------- OpenTDB (rate limited: 1 req / 5 s) ----------
def otdb_token():
    d = get("https://opentdb.com/api_token.php?command=request")
    return d.get("token") if d else None

def harvest_otdb(cfg, diff, seen, bucket, token):
    stalls = 0
    for cat in cfg.get("otdb", []):
        while len(bucket) < CAP and stalls < 3:
            url = (f"https://opentdb.com/api.php?amount=50&category={cat}"
                   f"&difficulty={diff}&type=multiple&encode=default")
            if token:
                url += f"&token={token}"
            time.sleep(5.2)                       # respect rate limit
            data = get(url)
            if not data:
                stalls += 1; continue
            rc = data.get("response_code")
            if rc in (3, 4):                       # token empty/not found -> next cat
                break
            if rc == 5:                            # rate limited
                time.sleep(6); continue
            new = 0
            for item in data.get("results", []):
                text = item.get("question", "")
                k = norm(clean(text))
                if not k or k in seen:
                    continue
                e = make_entry(text, item.get("correct_answer"),
                               item.get("incorrect_answers", []), diff)
                if e:
                    seen.add(k); bucket.append(e); new += 1
            stalls = stalls + 1 if new < 3 else 0
        stalls = 0

def main(topics):
    os.makedirs(OUT_DIR, exist_ok=True)
    token = otdb_token()
    for topic in topics:
        cfg = TOPICS[topic]
        seen, all_entries = set(), []
        for diff in DIFFS:
            bucket = []
            harvest_tapi(cfg, diff, seen, bucket)
            if len(bucket) < CAP:
                harvest_otdb(cfg, diff, seen, bucket, token)
            all_entries += bucket
            print(f"[{topic}] {diff}: {len(bucket)}", flush=True)
            json.dump({topic: all_entries},
                      open(f"{OUT_DIR}/{topic}.json", "w"), ensure_ascii=False, indent=1)
        counts = {d: sum(1 for e in all_entries if e["d"] == d) for d in DIFFS}
        print(f"== {topic} DONE: {counts} total {len(all_entries)} ==", flush=True)

if __name__ == "__main__":
    main(sys.argv[1:] or ["Geography", "History", "Hollywood"])
