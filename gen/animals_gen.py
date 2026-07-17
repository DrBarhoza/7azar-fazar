#!/usr/bin/env python3
"""Author OPEN-ENDED Animals questions from curated, accurate fact tables.
Output: gen/Animals.authored.json  ->  [{q,a,d,src:"authored"}]"""
import json, os
out = []
def add(q, a, d): out.append({"q": q, "a": a, "d": d, "src": "authored"})
def an(w): return ("an " if w[:1].lower() in "aeiou" else "a ") + w

# ---- animal class (kind) ----  easy=very common, medium/hard=less common
CLASS = {  # animal: (class phrase, difficulty)
 "dog":("A mammal","easy"),"cat":("A mammal","easy"),"cow":("A mammal","easy"),
 "horse":("A mammal","easy"),"lion":("A mammal","easy"),"elephant":("A mammal","easy"),
 "whale":("A mammal","easy"),"dolphin":("A mammal","medium"),"bat":("A mammal","medium"),
 "kangaroo":("A mammal","medium"),"tiger":("A mammal","easy"),"bear":("A mammal","easy"),
 "monkey":("A mammal","easy"),"rabbit":("A mammal","easy"),"giraffe":("A mammal","easy"),
 "eagle":("A bird","easy"),"owl":("A bird","easy"),"penguin":("A bird","easy"),
 "ostrich":("A bird","medium"),"parrot":("A bird","easy"),"flamingo":("A bird","medium"),
 "snake":("A reptile","easy"),"crocodile":("A reptile","easy"),"lizard":("A reptile","easy"),
 "turtle":("A reptile","medium"),"tortoise":("A reptile","medium"),"chameleon":("A reptile","medium"),
 "frog":("An amphibian","easy"),"toad":("An amphibian","medium"),"salamander":("An amphibian","hard"),
 "newt":("An amphibian","hard"),"shark":("A fish","easy"),"salmon":("A fish","medium"),
 "seahorse":("A fish","hard"),"eel":("A fish","hard"),"tuna":("A fish","medium"),
 "bee":("An insect","easy"),"ant":("An insect","easy"),"butterfly":("An insect","easy"),
 "beetle":("An insect","medium"),"grasshopper":("An insect","medium"),"dragonfly":("An insect","hard"),
 "spider":("An arachnid (not an insect)","medium"),"scorpion":("An arachnid","hard"),
 "crab":("A crustacean","medium"),"lobster":("A crustacean","hard"),"octopus":("A mollusc","hard"),
 "snail":("A mollusc","hard"),"starfish":("An echinoderm","hard"),
}
for a,(cls,d) in CLASS.items():
    add(f"What kind of animal is {an(a)}?", cls, d)

# ---- baby animal names ----
BABY = {"dog":"A puppy","cat":"A kitten","cow":"A calf","horse":"A foal","sheep":"A lamb",
 "goat":"A kid","lion":"A cub","bear":"A cub","tiger":"A cub","deer":"A fawn",
 "kangaroo":"A joey","frog":"A tadpole","chicken":"A chick","duck":"A duckling",
 "swan":"A cygnet","elephant":"A calf","whale":"A calf","seal":"A pup","goose":"A gosling",
 "pig":"A piglet","rabbit":"A kit","fox":"A kit","owl":"An owlet","eagle":"An eaglet",
 "horse (male)":"A colt","kangaroo (in pouch)":"A joey","hen (young)":"A chick"}
BABY_D = {"dog":"easy","cat":"easy","cow":"easy","horse":"easy","sheep":"easy","goat":"medium",
 "lion":"easy","bear":"medium","tiger":"medium","deer":"medium","kangaroo":"easy","frog":"easy",
 "chicken":"easy","duck":"easy","swan":"hard","elephant":"medium","whale":"medium","seal":"hard",
 "goose":"hard","pig":"easy","rabbit":"hard","fox":"hard","owl":"hard","eagle":"hard"}
for a,b in BABY.items():
    if a in BABY_D: add(f"What is a baby {a} called?", b, BABY_D[a])

# ---- collective nouns (group names) ----
GROUP = {"lions":("A pride","medium"),"wolves":("A pack","medium"),"fish":("A school","easy"),
 "birds":("A flock","easy"),"sheep":("A flock","easy"),"cattle":("A herd","easy"),
 "cows":("A herd","easy"),"crows":("A murder","hard"),"geese":("A gaggle","hard"),
 "bees":("A swarm","medium"),"ants":("A colony","medium"),"whales":("A pod","medium"),
 "dolphins":("A pod","medium"),"elephants":("A herd","easy"),"monkeys":("A troop","hard"),
 "kangaroos":("A mob","hard"),"owls":("A parliament","hard"),"ravens":("An unkindness","hard"),
 "puppies":("A litter","medium"),"kittens":("A litter","medium"),"lions (young)":("A litter","hard"),
 "wolves (young)":("A litter","hard"),"horses":("A herd","easy"),"chickens":("A flock","easy")}
for a,(g,d) in GROUP.items():
    add(f"What do you call a group of {a}?", g, d)

# ---- sounds ----
SOUND = {"dog":("Bark","easy"),"cat":("Meow","easy"),"cow":("Moo","easy"),"horse":("Neigh","easy"),
 "sheep":("Bleat","easy"),"pig":("Oink","easy"),"duck":("Quack","easy"),"lion":("Roar","easy"),
 "wolf":("Howl","medium"),"frog":("Croak","easy"),"bee":("Buzz","easy"),"snake":("Hiss","easy"),
 "owl":("Hoot","easy"),"rooster":("Crow","medium"),"donkey":("Bray","hard"),
 "elephant":("Trumpet","medium"),"mouse":("Squeak","medium"),"cricket":("Chirp","medium")}
for a,(s,d) in SOUND.items():
    add(f"What sound does {an(a)} make?", s, d)

# ---- diet type ----
DIET = {"lion":("Carnivore","easy"),"tiger":("Carnivore","medium"),"cow":("Herbivore","easy"),
 "sheep":("Herbivore","medium"),"rabbit":("Herbivore","easy"),"giraffe":("Herbivore","medium"),
 "elephant":("Herbivore","medium"),"bear":("Omnivore","medium"),"pig":("Omnivore","medium"),
 "human":("Omnivore","medium"),"shark":("Carnivore","medium"),"wolf":("Carnivore","medium"),
 "deer":("Herbivore","medium"),"panda":("Herbivore (mostly bamboo)","medium"),
 "eagle":("Carnivore","medium"),"chicken":("Omnivore","hard"),"horse":("Herbivore","easy"),
 "crocodile":("Carnivore","medium"),"koala":("Herbivore (eats eucalyptus)","hard")}
for a,(t,d) in DIET.items():
    add(f"Is {an(a)} a herbivore, carnivore, or omnivore?", t, d)

# ---- superlatives & classic facts ----
FACTS = [
 ("What is the fastest land animal?","The cheetah","easy"),
 ("What is the largest animal on Earth?","The blue whale","easy"),
 ("What is the tallest animal in the world?","The giraffe","easy"),
 ("What is the largest land animal?","The African elephant","easy"),
 ("Which is the only mammal that can truly fly?","The bat","medium"),
 ("What is the fastest bird (in a dive)?","The peregrine falcon","hard"),
 ("What is the largest fish in the world?","The whale shark","medium"),
 ("Which animal is known as the King of the Jungle?","The lion","easy"),
 ("How many legs does a spider have?","Eight","easy"),
 ("How many legs does an insect have?","Six","easy"),
 ("How many hearts does an octopus have?","Three","hard"),
 ("Which animal can change the colour of its skin to blend in?","The chameleon","medium"),
 ("What is the largest bird in the world?","The ostrich","medium"),
 ("Which large bird cannot fly and lives in Africa?","The ostrich","medium"),
 ("What is the slowest animal, known for hanging in trees?","The sloth","medium"),
 ("Which sea animal has eight arms?","The octopus","easy"),
 ("What is a group of lions called?","A pride","medium"),
 ("Which animal is famous for its black and white stripes?","The zebra","easy"),
 ("Which bird is a symbol of the United States?","The bald eagle","medium"),
 ("Which animal has a long trunk?","The elephant","easy"),
 ("Which animal carries its baby in a pouch?","The kangaroo","easy"),
 ("Which insect makes honey?","The bee","easy"),
 ("Which animal is known as man's best friend?","The dog","easy"),
 ("What do bees collect from flowers to make honey?","Nectar","medium"),
 ("Which animal has the longest neck?","The giraffe","easy"),
 ("Which big cat is the largest in the world?","The tiger","medium"),
 ("Which animal sleeps standing up?","The horse","medium"),
 ("Which animals build dams in rivers?","Beavers","medium"),
 ("What is the largest species of penguin?","The emperor penguin","hard"),
 ("Which animal is known for never forgetting, according to a saying?","The elephant","medium"),
 ("Which reptile can regrow its tail?","The lizard","medium"),
 ("Which mammal lays eggs?","The platypus","hard"),
 ("Which bird is known for copying human speech?","The parrot","easy"),
 ("What do you call an animal that is active at night?","Nocturnal","medium"),
 ("What do you call an animal that eats only plants?","A herbivore","easy"),
 ("What do you call an animal that eats only meat?","A carnivore","easy"),
 ("What do you call an animal that eats both plants and meat?","An omnivore","medium"),
 ("Which animal is the tallest and eats leaves from tall trees?","The giraffe","easy"),
 ("Which fish is famous for being able to give small electric shocks?","The electric eel","hard"),
 ("Which animal has a hump on its back and lives in the desert?","The camel","easy"),
 ("Which black-and-white animal from China eats bamboo?","The giant panda","easy"),
 ("Which ocean animal is a mammal and is very intelligent?","The dolphin","easy"),
 ("Which insect can lift many times its own body weight?","The ant","medium"),
 ("What is the largest type of bear?","The polar bear","medium"),
 ("Where do polar bears mainly live?","The Arctic","medium"),
 ("Which animal is famous for its spots and lives in Africa?","The leopard (or cheetah)","medium"),
 ("Which small animal stores nuts for the winter?","The squirrel","easy"),
 ("Which animal is known for its excellent memory and large ears?","The elephant","easy"),
 ("How many legs does a crab have in total?","Ten","hard"),
 ("What is the scientific study of insects called?","Entomology","medium"),
 ("Which branch of science is the study of insects?","Entomology","medium"),
]
for q,a,d in FACTS:
    add(q, a, d)

# dedup
seen, uniq = set(), []
for e in out:
    k = e["q"].lower()
    if k not in seen: seen.add(k); uniq.append(e)
from collections import Counter
c = Counter(e["d"] for e in uniq)
json.dump(uniq, open(os.path.join(os.path.dirname(__file__), "Animals.authored.json"), "w"),
          ensure_ascii=False, indent=1)
print(f"Animals authored: {len(uniq)}  (easy={c['easy']} medium={c['medium']} hard={c['hard']})")
