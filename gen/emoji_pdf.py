#!/usr/bin/env python3
"""Parse the user's Country Emoji Guessing Game PDF into open-ended questions.
Output: gen/EmojiPdf.authored.json"""
import json, re
from pypdf import PdfReader

PDF = "/Users/el-professor/Downloads/country_emoji_guessing_game (1).pdf"
OUT = "/Users/el-professor/Downloads/7azar-fazar/gen/EmojiPdf.authored.json"

# difficulty per clue number (my rating of how cryptic the rebus is)
DIFF = {1:"medium",2:"hard",3:"easy",4:"medium",5:"medium",6:"easy",7:"medium",8:"medium",
 9:"hard",10:"medium",11:"medium",12:"easy",13:"medium",14:"medium",15:"easy",16:"medium",
 17:"hard",18:"medium",19:"hard",20:"hard",21:"medium",22:"hard",23:"hard",24:"medium",
 25:"easy",26:"medium",27:"medium",28:"medium",29:"hard",30:"easy",31:"hard",32:"easy",
 33:"medium",34:"easy",35:"hard",36:"hard",37:"medium",38:"hard",39:"easy",40:"medium"}

text = PdfReader(PDF).pages[0].extract_text()
lines = text.split("\n")
# keep only the data region (between the header row and the footer)
start = next(i for i,l in enumerate(lines) if l.strip().startswith("# Emoji")) + 1
end = next((i for i,l in enumerate(lines) if "Final corrected" in l), len(lines))
data = [l for l in lines[start:end]]

INT = re.compile(r"^\d{1,2}$")
entries = {}
# rows come in groups of 3 lines: [L# +emojiL] [ansL  R# +emojiR] [ansR]
i = 0
rows = [data[j:j+3] for j in range(0, len(data)-2, 3)]
for a, b, c in rows:
    la = a.strip().split(" ", 1)
    lnum, lemoji = la[0], (la[1] if len(la) > 1 else "")
    bt = b.strip().split()
    # find the right-column number token inside line b
    ri = next(k for k,t in enumerate(bt) if INT.match(t))
    lans = " ".join(bt[:ri]).strip()
    rnum = bt[ri]
    remoji = " ".join(bt[ri+1:]).strip()
    rans = c.strip()
    for num, emoji, ans in ((lnum, lemoji, lans), (rnum, remoji, rans)):
        if INT.match(num) and emoji and ans:
            entries[int(num)] = (emoji.strip(), ans.strip())

out = []
for num in sorted(entries):
    emoji, ans = entries[num]
    out.append({"q": f"Which country? {emoji}", "a": ans, "d": DIFF.get(num, "medium"), "src": "authored"})

json.dump(out, open(OUT, "w"), ensure_ascii=False, indent=1)
print(f"parsed {len(out)} emoji puzzles")
for e in out:
    print(f"  {e['d'][:1]}  {e['q']}  ->  {e['a']}")
