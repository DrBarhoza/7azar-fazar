# 7azar Fazar — Family Quiz Battle 🎯

7azar Fazar (حزر فزر — "guess!") is a party quiz game for two teams, in the spirit
of classic Arabic TV quiz shows. One person hosts on a shared screen (laptop / TV);
teams answer out loud and the host judges.

## How to play

1. Open `index.html` in any browser (just double-click it — no install needed).
2. Enter the two team names.
3. Pick up to **6 topics**. Each selected topic shows a **×N box** where you
   choose how many questions that topic holds (an even number, 2–12), shared
   between both teams. Within a topic the questions climb in difficulty:
   🟢 Easy (10 pts) → 🟡 Medium (20 pts) → 🔴 Hard (30 pts).
4. Set the timer (15–60 s) and the steal rule.
5. Press **Start Game** to reveal the **board**: one column per topic, one tile
   per question showing its points and difficulty.
6. **Teams take turns picking.** Team 1 chooses any open tile, plays it, then
   Team 2 chooses, and so on until the board is empty. Since each topic holds an
   even number of questions, the two teams get the same number of turns.
7. After picking a tile, a "Get ready" screen shows the topic, the team, and what
   the question is worth — press **Go!** to start the clock.
8. The host reads the question. **Both teams say their answer out loud** — the
   team whose turn it is first, then the other team. While this happens the only
   button on screen is **👁 Reveal answer**, so nothing is scored yet.
9. The host presses **👁 Reveal answer**. The answer appears, the clock stops,
   and the judging buttons take its place:
   - **✓ Correct** — the team whose turn it is got it: full points, and a
     celebration video plays on medium and hard questions.
   - **✗ Wrong** — nobody got it: no points, and a booing video plays.
   - **🔁 Steal** — the *other* team got it: they take half the points, quietly
     (no video). Stealing does not change whose turn it is to pick next. The
     button is hidden when the steal rule is set to Disabled.

   Then the board returns for the other team's pick.

   **Year questions are judged loosely:** when the answer is a year, the card
   also shows the window to accept — `✓ 1492  (accept 1491 – 1493)`. A year
   either side counts, so "1491" is a correct answer to a 1492 question. This
   applies to the El-Barahma photo round's 📅 WHEN as well.
10. **Swap rule:** a team that doesn't like its question can pay **5 points** to
    swap it for another question of the same topic and difficulty (🔄 button).
    The timer restarts with the new question. Only available before the answer is
    revealed — you can't trade away a question you've already seen the answer to.
11. Highest score once the board is empty wins. 🏆

## Banning bad questions

If a question turns out to be unsuitable (confusing, broken, or it secretly
needs a picture), press **🚫 Ban this question** during the game. It's removed
permanently — even if you re-import the same question file — and a replacement
of the same difficulty is drawn on the spot so no one loses a turn. Change your
mind later with **♻️ Restore banned questions** on the setup screen.

## Repeat game nights

The game remembers which questions have been played (saved in the browser) and
serves fresh ones first. Each topic chip shows how many unused questions remain
(e.g. "10/12 new"). When a topic runs low, played questions return — or press
**🧠 Forget played questions** on the setup screen to reset the history.

## Loading your own questions

The game ships with sample questions, but you can load your own bank from a
**Word file (.docx)** or a **JSON file** — via the file button or a URL.
Loaded questions are saved in the browser, so you only load once.

### Word file format

See `question-bank-template.docx` for a ready-made template. The rules:

```
TOPIC: Geography
Q(easy): What is the longest river in the world?
A: The Nile
Q(medium): Which desert covers most of northern Africa?
A: The Sahara
Q(hard): What is the largest island in the world?
A: Greenland
```

- A line starting with `TOPIC:` begins a new topic.
- Each question is a `Q(easy):` / `Q(medium):` / `Q(hard):` line followed by an
  `A:` line. A plain `Q:` counts as medium.
- Questions may wrap onto several lines; the answer line ends them.
- Each team gets one easy, one medium and one hard question per topic, so give
  every topic **at least 2 of each tier** — more if you want spares for future
  game nights.
- Any other text (titles, notes) is ignored.

### JSON format

```json
{
  "Geography": [
    { "q": "What is the longest river in the world?", "a": "The Nile", "d": "easy" }
  ]
}
```

`"d"` is `"easy"`, `"medium"` or `"hard"` (or 1/2/3); it defaults to medium.
A question may also set:

- `"t"` — its own time limit in seconds (5–900), overriding the game's timer.
  The bundled `kangaroo-questions.json` uses easy = 1 min, medium = 3 min,
  hard = 5 min.
- `"img"` — a picture to show with the question, given as a path relative to
  `index.html` (e.g. `"kangaroo-figures/2018_Benjamin_01.jpg"`) or a `data:` URI.

## The Math Kangaroo topic

`kangaroo-questions.json` holds **848 questions** taken from the Math Kangaroo
papers (2009–2024) at [matematica.pt](https://www.matematica.pt/en/useful/kangaroo-questions.php),
with the competition level setting the difficulty: Écolier = easy, Benjamin =
medium, Kadett = hard.

Many Kangaroo problems depend on a diagram. For those, the question card is
shown as an **image cropped straight from the original paper** (in
`kangaroo-figures/`), so the drawing, the wording, and the five options are all
visible. Keep that folder next to `index.html`.

The crops are produced automatically and a few are imperfect — a figure may be
clipped at a page edge, or a neighbouring question may appear underneath. When
that happens, press **🚫 Ban this question**: it is removed for good and a
replacement is dealt immediately.

### Loading from a URL

Paste a link to a `.docx` or `.json` and press **Fetch**. Note: the file must be
served with CORS enabled (raw GitHub links work well; Google Drive / OneDrive
share links usually don't — download the file and use the file button instead).

## Files

- `index.html` — the whole game (open this)
- `question-bank-template.docx` — starter template for your question bank

Internet is only needed the first time you load a `.docx` (the Word-file reader
library loads from a CDN). Playing and JSON loading work fully offline.
