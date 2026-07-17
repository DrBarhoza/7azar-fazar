#!/usr/bin/env python3
"""Author OPEN-ENDED Medicine / human-body questions from curated accurate facts.
Output: gen/Medicine.authored.json -> [{q,a,d,src:"authored"}]"""
import json, os
from collections import Counter
out = []
def add(q, a, d): out.append({"q": q, "a": a, "d": d, "src": "authored"})

FACTS = [
 # ---- easy: basic body facts a child knows ----
 ("Which organ pumps blood around the body?","The heart","easy"),
 ("Which organs do we use to breathe?","The lungs","easy"),
 ("Which organ do we use to think?","The brain","easy"),
 ("Which organ digests the food we eat?","The stomach","easy"),
 ("What is the largest organ of the human body?","The skin","easy"),
 ("Which part of the body do we use to see?","The eyes","easy"),
 ("Which part of the body do we use to hear?","The ears","easy"),
 ("Which part of the body do we use to smell?","The nose","easy"),
 ("Which part of the body do we use to taste?","The tongue","easy"),
 ("How many senses does the human body have?","Five","easy"),
 ("How many lungs does a person have?","Two","easy"),
 ("What gas do we breathe in that our body needs?","Oxygen","easy"),
 ("What do our bones do for our body?","Support it and give it shape","easy"),
 ("What are teeth used for?","Biting and chewing food","easy"),
 ("Which red liquid flows through our veins?","Blood","easy"),
 ("What should you do to keep your teeth healthy?","Brush them","easy"),
 ("Which part of the body pumps and is felt as a heartbeat?","The heart","easy"),
 ("What covers and protects the outside of our body?","The skin","easy"),
 ("Which part of your body helps you balance and walk?","The legs","easy"),
 ("What do we call the doctor who looks after our teeth?","A dentist","easy"),
 # ---- medium: systems, counts, specialties ----
 ("How many bones are in the adult human body?","206","medium"),
 ("How many teeth does a typical adult have?","32","medium"),
 ("How many chambers does the human heart have?","Four","medium"),
 ("Which body system includes the heart and blood vessels?","The circulatory system","medium"),
 ("Which body system includes the lungs?","The respiratory system","medium"),
 ("Which body system includes the brain and nerves?","The nervous system","medium"),
 ("Which body system is made of all the bones?","The skeletal system","medium"),
 ("Which body system is made of muscles?","The muscular system","medium"),
 ("Which body system breaks down food?","The digestive system","medium"),
 ("Which organ filters the blood and makes urine?","The kidneys","medium"),
 ("Which organ cleans the blood and removes toxins?","The liver","medium"),
 ("What is the medical name for the windpipe?","The trachea","medium"),
 ("What is the medical name for the voice box?","The larynx","medium"),
 ("Which cells in the blood carry oxygen?","Red blood cells","medium"),
 ("Which cells in the blood fight infection?","White blood cells","medium"),
 ("Which vitamin does the body make from sunlight?","Vitamin D","medium"),
 ("Which vitamin is found in oranges and lemons?","Vitamin C","medium"),
 ("What mineral makes our bones and teeth strong?","Calcium","medium"),
 ("What gas do we breathe out?","Carbon dioxide","medium"),
 ("What protects the brain?","The skull","medium"),
 ("What protects the heart and lungs?","The ribcage","medium"),
 ("What carries messages around the body?","The nerves","medium"),
 ("What is a doctor who treats the heart called?","A cardiologist","medium"),
 ("What is a doctor who treats the skin called?","A dermatologist","medium"),
 ("What is a doctor for children called?","A pediatrician","medium"),
 ("What is a doctor who treats animals called?","A veterinarian","medium"),
 ("Roughly what is normal human body temperature in Celsius?","About 37°C","medium"),
 ("How many baby (milk) teeth do children have?","20","medium"),
 ("What connects muscles to bones?","Tendons","medium"),
 ("What do we call the see-through front part of the eye?","The cornea","medium"),
 ("Which organ produces the most heat in the body?","The liver","medium"),
 ("Which part of the eye controls how much light enters?","The pupil (and iris)","medium"),
 # ---- hard: specific names & deeper facts ----
 ("What is the longest and strongest bone in the human body?","The femur (thigh bone)","hard"),
 ("What is the smallest bone in the human body?","The stapes (in the ear)","hard"),
 ("How many pairs of ribs does a human have?","12 pairs (24 ribs)","hard"),
 ("Which organ produces insulin?","The pancreas","hard"),
 ("What is the liquid part of blood called?","Plasma","hard"),
 ("Which blood type is known as the universal donor?","O negative","hard"),
 ("What helps the blood to clot?","Platelets","hard"),
 ("What is the 'funny bone' actually?","A nerve (the ulnar nerve)","hard"),
 ("Which gland is called the body's 'master gland'?","The pituitary gland","hard"),
 ("What is the strongest muscle for its size in the body?","The jaw muscle (masseter)","hard"),
 ("What is the largest muscle in the human body?","The gluteus maximus (in the buttock)","hard"),
 ("Which disease is caused by a lack of vitamin C?","Scurvy","hard"),
 ("What is the medical name for the collarbone?","The clavicle","hard"),
 ("What is the medical name for the kneecap?","The patella","hard"),
 ("What is the medical name for red blood cell count that is too low?","Anaemia","hard"),
 ("Which part of the brain controls balance and coordination?","The cerebellum","hard"),
 ("What is the largest artery in the body?","The aorta","hard"),
 ("How many bones is a baby born with, roughly?","About 300","hard"),
 ("What is the name of the tube that carries urine out of the body?","The urethra","hard"),
 ("Which organ can regrow part of itself if damaged?","The liver","hard"),
 ("What is the medical term for high blood pressure?","Hypertension","hard"),
 ("What is a doctor who performs operations called?","A surgeon","hard"),
 ("What is a doctor who treats the brain and nerves called?","A neurologist","hard"),
 ("What is a doctor who treats bones and joints called?","An orthopaedist","hard"),
 ("Which vitamin helps blood to clot?","Vitamin K","hard"),
 ("What is the medical name for the breastbone?","The sternum","hard"),
 ("What is the medical name for a nosebleed?","Epistaxis","hard"),
 ("Which part of blood carries oxygen using iron?","Haemoglobin","hard"),
]
for q,a,d in FACTS:
    add(q, a, d)

seen, uniq = set(), []
for e in out:
    k = e["q"].lower()
    if k not in seen: seen.add(k); uniq.append(e)
c = Counter(e["d"] for e in uniq)
json.dump(uniq, open(os.path.join(os.path.dirname(__file__), "Medicine.authored.json"), "w"),
          ensure_ascii=False, indent=1)
print(f"Medicine authored: {len(uniq)}  (easy={c['easy']} medium={c['medium']} hard={c['hard']})")
