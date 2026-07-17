#!/usr/bin/env python3
"""Generate accurate EASY geography questions (for ~10-year-olds) from curated
data. Output: gen/Geography.easy.json  as [{q,a,d:"easy"}] multiple-choice."""
import json, random, os
random.seed(42)
random.seed  # deterministic

CONTINENTS = ["Africa", "Asia", "Europe", "North America", "South America", "Oceania"]

# well-known country -> continent (easy tier: only famous countries)
COUNTRY_CONT = {
 "France":"Europe","Germany":"Europe","Italy":"Spain and","Spain":"Europe","England":"Europe",
 "Greece":"Europe","Portugal":"Europe","Norway":"Europe","Sweden":"Europe","Poland":"Europe",
 "Ireland":"Europe","Switzerland":"Europe","Austria":"Europe","Netherlands":"Europe",
 "China":"Asia","Japan":"Asia","India":"Asia","Thailand":"Asia","Vietnam":"Asia",
 "South Korea":"Asia","Indonesia":"Asia","Saudi Arabia":"Asia","Iraq":"Asia","Iran":"Asia",
 "Philippines":"Asia","Malaysia":"Asia","Nepal":"Asia","Pakistan":"Asia",
 "Egypt":"Africa","Nigeria":"Africa","Kenya":"Africa","Morocco":"Africa","South Africa":"Africa",
 "Ghana":"Africa","Ethiopia":"Africa","Algeria":"Africa","Tanzania":"Africa","Uganda":"Africa",
 "United States":"North America","Canada":"North America","Mexico":"North America",
 "Cuba":"North America","Jamaica":"North America","Panama":"North America","Costa Rica":"North America",
 "Brazil":"South America","Argentina":"South America","Chile":"South America","Peru":"South America",
 "Colombia":"South America","Venezuela":"South America","Ecuador":"South America","Uruguay":"South America",
 "Australia":"Oceania","New Zealand":"Oceania","Fiji":"Oceania",
}
COUNTRY_CONT["Italy"] = "Europe"  # fix

# landmark -> country
LANDMARKS = {
 "the Eiffel Tower":"France","Big Ben":"England","the Colosseum":"Italy","the Great Wall":"China",
 "the Taj Mahal":"India","the Pyramids of Giza":"Egypt","the Statue of Liberty":"the United States",
 "Christ the Redeemer":"Brazil","Machu Picchu":"Peru","the Sydney Opera House":"Australia",
 "the Leaning Tower of Pisa":"Italy","the Acropolis":"Greece","the Sagrada Familia":"Spain",
 "Mount Fuji":"Japan","Petra":"Jordan","the Burj Khalifa":"the United Arab Emirates",
 "Stonehenge":"England","the Brandenburg Gate":"Germany","the Kremlin":"Russia",
 "the Great Barrier Reef":"Australia","Table Mountain":"South Africa","the Golden Gate Bridge":"the United States",
 "Angkor Wat":"Cambodia","the Parthenon":"Greece","Niagara Falls":"Canada","the Little Mermaid statue":"Denmark",
 "Mount Kilimanjaro":"Tanzania","the Sphinx":"Egypt","Buckingham Palace":"England","the Louvre":"France",
}
COUNTRY_POOL = ["France","Italy","Spain","China","Japan","India","Egypt","Brazil","Peru",
 "Australia","Greece","Germany","Russia","Canada","Mexico","England","the United States",
 "Kenya","Jordan","Cambodia","Denmark","Tanzania","South Africa","the United Arab Emirates"]

# main language of well-known countries (accurate, stable)
LANGUAGES = {
 "Brazil":"Portuguese","Mexico":"Spanish","Argentina":"Spanish","Egypt":"Arabic",
 "Saudi Arabia":"Arabic","Japan":"Japanese","China":"Mandarin Chinese","France":"French",
 "Germany":"German","Italy":"Italian","Russia":"Russian","Greece":"Greek","Portugal":"Portuguese",
 "Netherlands":"Dutch","Iran":"Persian","Turkey":"Turkish","Thailand":"Thai","Vietnam":"Vietnamese",
 "South Korea":"Korean","Sweden":"Swedish","Norway":"Norwegian","Poland":"Polish","India":"Hindi",
}
LANG_POOL = ["English","Spanish","French","Arabic","Portuguese","German","Italian","Russian",
 "Japanese","Korean","Mandarin Chinese","Dutch","Greek","Turkish","Thai","Polish","Swedish"]

# currency of well-known countries (accurate, stable)
CURRENCIES = {
 "Japan":"the Yen","the United States":"the Dollar","India":"the Rupee","Russia":"the Ruble",
 "China":"the Yuan","Mexico":"the Peso","Brazil":"the Real","Egypt":"the Egyptian Pound",
 "Saudi Arabia":"the Riyal","South Africa":"the Rand","Switzerland":"the Swiss Franc",
 "Sweden":"the Krona","Turkey":"the Lira","Thailand":"the Baht","South Korea":"the Won",
 "France":"the Euro","Germany":"the Euro","Italy":"the Euro","Spain":"the Euro","Greece":"the Euro",
}
CUR_POOL = ["the Dollar","the Euro","the Yen","the Pound","the Rupee","the Peso","the Real",
 "the Ruble","the Yuan","the Franc","the Krona","the Lira","the Baht","the Won","the Rand"]

# which-is-bigger / simple comparison facts
COMPARISONS = [
 ("Which is bigger in area, Russia or Canada?","Russia",["Canada","They are the same","Neither is large"]),
 ("Which is bigger in area, the United States or Mexico?","the United States",["Mexico","They are equal","Neither"]),
 ("Which country is bigger in area, China or Japan?","China",["Japan","They are equal","Neither"]),
 ("Which is larger, the Pacific Ocean or the Atlantic Ocean?","the Pacific Ocean",["the Atlantic Ocean","They are equal","Neither"]),
 ("Which is taller, Mount Everest or Mont Blanc?","Mount Everest",["Mont Blanc","They are equal","Neither"]),
 ("Which continent is bigger, Asia or Africa?","Asia",["Africa","They are equal","Neither"]),
 ("Which continent is bigger, Europe or Australia?","Europe",["Australia","They are equal","Neither"]),
 ("Which country has more people, India or Australia?","India",["Australia","They are equal","Neither"]),
 ("Which river is longer, the Nile or the Thames?","the Nile",["the Thames","They are equal","Neither"]),
 ("Which is colder on average, Antarctica or Africa?","Antarctica",["Africa","They are equal","Neither"]),
 ("Which is closer to the Equator, Brazil or Norway?","Brazil",["Norway","They are equal","Neither"]),
 ("Which country is farther north, Egypt or Sweden?","Sweden",["Egypt","They are equal","Neither"]),
]

# classic single-fact questions: (question, correct, [distractors])
FACTS = [
 ("What is the largest ocean on Earth?","the Pacific Ocean",["the Atlantic Ocean","the Indian Ocean","the Arctic Ocean"]),
 ("What is the smallest ocean on Earth?","the Arctic Ocean",["the Indian Ocean","the Atlantic Ocean","the Pacific Ocean"]),
 ("What is the longest river in the world?","the Nile",["the Amazon","the Mississippi","the Yangtze"]),
 ("What is the tallest mountain in the world?","Mount Everest",["K2","Mont Blanc","Kilimanjaro"]),
 ("What is the largest country in the world by area?","Russia",["Canada","China","the United States"]),
 ("What is the smallest country in the world?","Vatican City",["Monaco","Malta","San Marino"]),
 ("Which is the largest continent?","Asia",["Africa","Europe","North America"]),
 ("Which is the smallest continent?","Oceania (Australia)",["Europe","Antarctica","South America"]),
 ("Which is the coldest continent?","Antarctica",["Europe","Asia","North America"]),
 ("Which is the largest hot desert in the world?","the Sahara",["the Gobi","the Kalahari","the Arabian Desert"]),
 ("What is the largest rainforest in the world?","the Amazon",["the Congo","the Daintree","the Taiga"]),
 ("What is the largest island in the world?","Greenland",["Australia","Madagascar","Borneo"]),
 ("Which country has the most people in the world?","India",["China","the United States","Indonesia"]),
 ("Which sea is so salty you float easily in it?","the Dead Sea",["the Red Sea","the Black Sea","the Caspian Sea"]),
 ("On which continent is the Sahara Desert?","Africa",["Asia","Australia","South America"]),
 ("On which continent is the Amazon River?","South America",["Africa","Asia","North America"]),
 ("Which country is shaped like a boot?","Italy",["Spain","Greece","Portugal"]),
 ("Through which country does the Nile mainly flow?","Egypt",["Kenya","Nigeria","Morocco"]),
 ("Which two countries border Mount Everest?","Nepal and China",["India and China","Nepal and India","Bhutan and China"]),
 ("What is the largest country in South America?","Brazil",["Argentina","Peru","Chile"]),
 ("What is the largest country in Africa by area?","Algeria",["Egypt","Nigeria","South Africa"]),
 ("Which ocean lies between America and Europe?","the Atlantic Ocean",["the Pacific Ocean","the Indian Ocean","the Arctic Ocean"]),
 ("Which line divides the Earth into Northern and Southern halves?","the Equator",["the Prime Meridian","the Tropic of Cancer","the International Date Line"]),
 ("What do we call a piece of land surrounded by water on all sides?","an island",["a peninsula","a cape","an isthmus"]),
 ("What do we call molten rock that comes out of a volcano?","lava",["magma","ash","sediment"]),
 ("Which country is both a country and a continent?","Australia",["Greenland","India","Russia"]),
 ("What is the capital city of France?","Paris",["London","Rome","Madrid"]),
 ("What is the capital city of Japan?","Tokyo",["Beijing","Seoul","Bangkok"]),
 ("What is the capital city of Egypt?","Cairo",["Nairobi","Rabat","Tripoli"]),
 ("What is the capital city of the United States?","Washington, D.C.",["New York","Los Angeles","Chicago"]),
 ("What is the capital city of Italy?","Rome",["Milan","Venice","Naples"]),
 ("Which country has the Great Barrier Reef off its coast?","Australia",["New Zealand","Indonesia","the Philippines"]),
 ("Which continent are penguins mostly found on in the wild?","Antarctica",["the Arctic","Europe","Asia"]),
 ("What is the name of the imaginary line at 0° longitude?","the Prime Meridian",["the Equator","the Tropic of Capricorn","the Date Line"]),
 ("Which country has the most islands in the world?","Sweden",["Indonesia","Canada","the Philippines"]),
 ("What is the hottest continent on average?","Africa",["Asia","South America","Australia"]),
 ("Which mountain range separates Europe from Asia?","the Ural Mountains",["the Alps","the Andes","the Himalayas"]),
 ("What is the longest mountain range in the world?","the Andes",["the Rockies","the Himalayas","the Alps"]),
 ("Which country is home to the kangaroo?","Australia",["South Africa","Brazil","India"]),
 ("Which desert covers much of Mongolia and China?","the Gobi Desert",["the Sahara","the Kalahari","the Atacama"]),
]

def mc(q, correct, distractors, d="easy"):
    opts = [correct] + distractors[:3]
    random.shuffle(opts)
    ci = opts.index(correct)
    text = q + "  " + "  ".join(f"({chr(65+i)}) {o}" for i, o in enumerate(opts))
    return {"q": text, "a": f"{chr(65+ci)}) {correct}", "d": d}

out = []
# continent questions
for country, cont in COUNTRY_CONT.items():
    if cont not in CONTINENTS:
        continue
    dist = random.sample([c for c in CONTINENTS if c != cont], 3)
    out.append(mc(f"On which continent is {country}?", cont, dist))
# landmark questions
for lm, country in LANDMARKS.items():
    dist = random.sample([c for c in COUNTRY_POOL if c != country], 3)
    out.append(mc(f"In which country would you find {lm}?", country, dist))
# classic facts
for q, correct, dist in FACTS:
    out.append(mc(q, correct, dist))
# comparisons
for q, correct, dist in COMPARISONS:
    out.append(mc(q, correct, dist))
# languages
for country, lang in LANGUAGES.items():
    dist = random.sample([l for l in LANG_POOL if l != lang], 3)
    out.append(mc(f"What is the main language spoken in {country}?", lang, dist))
# currencies
for country, cur in CURRENCIES.items():
    dist = random.sample([c for c in CUR_POOL if c != cur], 3)
    out.append(mc(f"What is the currency used in {country}?", cur, dist))

# dedup by question stem
seen, uniq = set(), []
for e in out:
    k = e["q"].split("  (A)")[0].lower()
    if k not in seen:
        seen.add(k); uniq.append(e)

os.makedirs(os.path.dirname(__file__), exist_ok=True)
json.dump(uniq, open(os.path.join(os.path.dirname(__file__), "Geography.easy.json"), "w"),
          ensure_ascii=False, indent=1)
print(f"generated {len(uniq)} easy geography questions")
