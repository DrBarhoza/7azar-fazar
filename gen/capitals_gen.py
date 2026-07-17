#!/usr/bin/env python3
"""Author Country Capitals (open-ended) + package the emoji 'Guess the Country'
puzzles. Outputs gen/Capitals.authored.json and gen/Emoji.authored.json."""
import json, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EASY = {
 "France":"Paris","United Kingdom":"London","Italy":"Rome","Spain":"Madrid","Germany":"Berlin",
 "Russia":"Moscow","China":"Beijing","Japan":"Tokyo","India":"New Delhi",
 "United States":"Washington, D.C.","Canada":"Ottawa","Brazil":"Brasília","Egypt":"Cairo",
 "Greece":"Athens","Australia":"Canberra","Mexico":"Mexico City","Argentina":"Buenos Aires",
 "Portugal":"Lisbon","Turkey":"Ankara","Cuba":"Havana","Ireland":"Dublin","Netherlands":"Amsterdam",
 "Belgium":"Brussels","Austria":"Vienna","Sweden":"Stockholm","Norway":"Oslo","Denmark":"Copenhagen",
 "Finland":"Helsinki","Poland":"Warsaw","Switzerland":"Bern","Thailand":"Bangkok","South Korea":"Seoul",
 "Saudi Arabia":"Riyadh","Kenya":"Nairobi","Nigeria":"Abuja","Morocco":"Rabat","Iraq":"Baghdad",
 "Iran":"Tehran","Indonesia":"Jakarta","Peru":"Lima","Chile":"Santiago","Colombia":"Bogotá",
 "New Zealand":"Wellington",
}
MEDIUM = {
 "Vietnam":"Hanoi","Philippines":"Manila","Malaysia":"Kuala Lumpur","Pakistan":"Islamabad",
 "Afghanistan":"Kabul","Ukraine":"Kyiv","Hungary":"Budapest","Czech Republic":"Prague",
 "Romania":"Bucharest","Bulgaria":"Sofia","Serbia":"Belgrade","Croatia":"Zagreb","Iceland":"Reykjavik",
 "Lebanon":"Beirut","Jordan":"Amman","Syria":"Damascus","Kuwait":"Kuwait City","Qatar":"Doha",
 "United Arab Emirates":"Abu Dhabi","Oman":"Muscat","Yemen":"Sana'a","Algeria":"Algiers",
 "Tunisia":"Tunis","Libya":"Tripoli","Sudan":"Khartoum","Ethiopia":"Addis Ababa","Ghana":"Accra",
 "Uganda":"Kampala","Zimbabwe":"Harare","Zambia":"Lusaka","Angola":"Luanda","Mozambique":"Maputo",
 "Senegal":"Dakar","Cameroon":"Yaoundé","Venezuela":"Caracas","Ecuador":"Quito","Paraguay":"Asunción",
 "Uruguay":"Montevideo","Guatemala":"Guatemala City","Costa Rica":"San José","Panama":"Panama City",
 "Dominican Republic":"Santo Domingo","Jamaica":"Kingston","Singapore":"Singapore","Nepal":"Kathmandu",
 "Bangladesh":"Dhaka","Mongolia":"Ulaanbaatar","Kazakhstan":"Astana","Uzbekistan":"Tashkent",
 "Azerbaijan":"Baku","Georgia":"Tbilisi","Armenia":"Yerevan","Slovakia":"Bratislava",
 "Slovenia":"Ljubljana","Lithuania":"Vilnius","Latvia":"Riga","Estonia":"Tallinn","Belarus":"Minsk",
 "Luxembourg":"Luxembourg City","Malta":"Valletta","Cyprus":"Nicosia","Albania":"Tirana",
 "North Macedonia":"Skopje","Bosnia and Herzegovina":"Sarajevo","Moldova":"Chișinău",
 "Honduras":"Tegucigalpa","Nicaragua":"Managua","El Salvador":"San Salvador",
 "South Africa":"Pretoria (administrative capital)",
}
HARD = {
 "Andorra":"Andorra la Vella","Liechtenstein":"Vaduz","Monaco":"Monaco","San Marino":"San Marino",
 "Montenegro":"Podgorica","Turkmenistan":"Ashgabat","Kyrgyzstan":"Bishkek","Tajikistan":"Dushanbe",
 "Bhutan":"Thimphu","Maldives":"Malé","Brunei":"Bandar Seri Begawan","East Timor":"Dili",
 "Papua New Guinea":"Port Moresby","Fiji":"Suva","Samoa":"Apia","Tonga":"Nuku'alofa",
 "Vanuatu":"Port Vila","Solomon Islands":"Honiara","Botswana":"Gaborone","Namibia":"Windhoek",
 "Lesotho":"Maseru","Eswatini":"Mbabane","Malawi":"Lilongwe","Rwanda":"Kigali","Burundi":"Gitega",
 "Djibouti":"Djibouti","Eritrea":"Asmara","Somalia":"Mogadishu","Chad":"N'Djamena","Niger":"Niamey",
 "Mali":"Bamako","Burkina Faso":"Ouagadougou","Mauritania":"Nouakchott","Gambia":"Banjul",
 "Guinea":"Conakry","Sierra Leone":"Freetown","Liberia":"Monrovia","Togo":"Lomé","Benin":"Porto-Novo",
 "Gabon":"Libreville","Republic of the Congo":"Brazzaville","Central African Republic":"Bangui",
 "South Sudan":"Juba","Equatorial Guinea":"Malabo","Cape Verde":"Praia","Comoros":"Moroni",
 "Seychelles":"Victoria","Mauritius":"Port Louis","Madagascar":"Antananarivo","Suriname":"Paramaribo",
 "Guyana":"Georgetown","Trinidad and Tobago":"Port of Spain","Barbados":"Bridgetown",
 "Bahamas":"Nassau","Belize":"Belmopan","Ivory Coast":"Yamoussoukro","Myanmar":"Naypyidaw",
 "Sri Lanka":"Sri Jayawardenepura Kotte (Colombo is the largest city)","Laos":"Vientiane",
 "Cambodia":"Phnom Penh","Democratic Republic of the Congo":"Kinshasa","Tanzania":"Dodoma",
 "Bolivia":"Sucre (La Paz is the seat of government)",
}
caps = []
for tier, tbl in (("easy", EASY), ("medium", MEDIUM), ("hard", HARD)):
    for country, cap in tbl.items():
        caps.append({"q": f"What is the capital of {country}?", "a": cap, "d": tier, "src": "authored"})
json.dump(caps, open(f"{BASE}/gen/Capitals.authored.json", "w"), ensure_ascii=False, indent=1)

# emoji rebus puzzles (carried over from the game's built-in 'Guess the Country')
EMOJI = [
 ("Which country? 🍕🍝","Italy","easy"),("Which country? 🦘🐨","Australia","easy"),
 ("Which country? 🍁","Canada","easy"),("Which country? 🗼🥖","France","easy"),
 ("Which country? 🦃","Turkey","medium"),("Which country? 🥶🌶️","Chile (chilly + chili)","medium"),
 ("Which country? 🧊🛬","Iceland (ice + landing)","medium"),("Which country? 🐟🛬","Finland (fin + landing)","medium"),
 ("Which country? 🍽️😋","Hungary (hungry)","hard"),("Which country? 🐄⏳","Kuwait (cow + wait)","hard"),
 ("Which country? 🦠👨‍👩‍👧‍👦","Germany (germ + many)","hard"),("Which country? 🕳️🛬","The Netherlands (hole + landing)","hard"),
]
emoji = [{"q": q, "a": a, "d": d, "src": "authored"} for q, a, d in EMOJI]
json.dump(emoji, open(f"{BASE}/gen/Emoji.authored.json", "w"), ensure_ascii=False, indent=1)

from collections import Counter
c = Counter(x["d"] for x in caps)
print(f"Capitals: {len(caps)} (easy={c['easy']} medium={c['medium']} hard={c['hard']}) | Emoji: {len(emoji)}")
