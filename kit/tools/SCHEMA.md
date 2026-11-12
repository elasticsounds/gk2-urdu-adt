# ADT page content schema (one file per PDF page: `content/pNNN.json`)

The book is the Punjab (Pakistan) Class 2 General Knowledge textbook "واقفیتِ عامہ", in Urdu.
We are turning it into an Accessible Digital Textbook (ADT). Each PDF page becomes one JSON file.
Learners are ~7 years old; many have disabilities (vision, hearing, motor, intellectual e.g. Down syndrome).

## Inputs you read for page NNN (3 digits, PDF page index, 1-based)
- `qa/read/pNNN_top.jpg` and `qa/read/pNNN_bottom.jpg` : 2x enlargements (top half / bottom half) — READ THESE to transcribe the Urdu accurately.
- `qa/grid/pNNN.jpg` : the page with a coordinate grid. Lines every 0.05; labels .1 … .9 are fractions of page width (x, left→right) and page height (y, top→bottom). Use it to work out crop boxes.

## Golden rules
1. **Transcribe Urdu faithfully.** Body text in `p`, `h`, `fact`, `teacher`, `note`, `list`, `table` blocks and every activity `orig` must be the book's own words, verbatim, in correct Unicode Urdu (ے ی ہ ھ ک گ ں ؤ ئ ۔ ، ؟ — never Arabic ي/ك/ه lookalikes). Keep the English words the book prints in brackets, e.g. `برِاعظم (Continent)`. You may split one long paragraph into 2–3 `p` blocks at sentence boundaries, but do not reword, summarise, or drop any sentence. If a word is truly illegible, give your best reading — never leave placeholders.
2. Everything you *add* (hints, easy-read, activity prompts/feedback, alt text, level variants) is written by you, in simple, warm, correct Pakistani Urdu a 7-year-old understands, plus an English translation in `en`.
3. Every text object is `{"ur": "...", "en": "..."}`. `en` is a plain English translation (used by reviewers).
4. Do not include decorative page furniture (sun, backpack, pencil, bell, stars, pink border, page number, cartoon teacher heads).
5. Reading order = the logical order a teacher would read the page (Urdu pages read right→left, top→bottom).
6. Valid JSON only (UTF-8, no comments, no trailing commas). Write Urdu characters directly, not \u escapes.

## Top-level object
```json
{
  "n": 6,                    // PDF page index
  "printed": "2",            // page number printed on the page ("" if none)
  "chapter": 1,              // 0 for front/back matter
  "kind": "content",         // cover | front | toc | opener | content | exercise | back
  "title": {"ur": "ہمارا وطن پاکستان", "en": "Our homeland Pakistan"},   // short page title for navigation (unique-ish; use the main heading or topic)
  "blocks": [ ... ],         // the adapted page, in reading order
  "hint": [ ... ],           // 2–4 helpful-hint items (see below)
  "easy": { ... },           // easy-read version (see below). Required for opener/content/exercise pages; null for cover/front/toc/back
  "print": true              // true if the page has something worth printing as a worksheet (any activity or exercise)
}
```

## Blocks
```json
{"t":"h",  "ur":"پاکستان کا پرچم", "en":"The flag of Pakistan"}
{"t":"p",  "ur":"…", "en":"…"}
{"t":"list", "items":[{"ur":"…","en":"…"}]}                       // bullet lists, e.g. learning outcomes on chapter openers
{"t":"img", "crop":[0.17,0.40,0.80,0.91], "alt":{"ur":"…","en":"…"}, "cap":{"ur":"…","en":"…"}}   // cap optional (use the printed caption, verbatim)
{"t":"gallery", "items":[{"crop":[…],"alt":{…},"cap":{…}}, …]}      // 2+ images that belong together (photo grids)
{"t":"fact", "ur":"…", "en":"…"}          // the "کیا آپ جانتے ہیں؟" (Do you know?) boxes — text only, without that label
{"t":"teacher", "ur":"…", "en":"…"}       // "برائے اساتذہ" (For teachers) boxes — text only, without that label
{"t":"note", "ur":"…", "en":"…"}          // footnotes / starred notes
{"t":"table", "head":[{"ur":"","en":""}], "rows":[[{"ur":"","en":""}]]}   // only for informational tables (not exercise tables)
{"t":"activity", …}                         // see Activities
```
**Crops** are `[x0, y0, x1, y1]` as fractions (0–1) of the page width/height, x0<x1, y0<y1. Crop the picture itself tightly (include its thin frame if any, exclude captions/text and page decorations). `alt` describes what is in the picture for a blind child (1 sentence; for maps/diagrams describe the information, 1–3 sentences). Every photo/illustration/map/diagram that carries meaning must appear as `img`/`gallery` (or inside an activity).
On chapter-opener pages: give the chapter number + title as `h`, "حاصلاتِ تعلّم" as `h`, the intro line as `p`, outcomes as `list`, and any photo as `img` if it is clean enough to crop.

## Activities
Every "سرگرمی" (activity) box and every "مشق" (exercise) question in the book becomes an `activity` block, placed where it appears on the page. One block per سرگرمی box / per "سوال نمبر".
```json
{
  "t": "activity",
  "id": "p013-a1",                       // pNNN-aK, unique
  "label": {"ur":"سوال نمبر 1","en":"Question 1"},     // "سرگرمی" / "سوال نمبر 2" / "مشق" …
  "orig":  {"ur":"…book's instruction and question text, verbatim…","en":"…"},
  "prompt":{"ur":"…child-friendly instruction for the interactive version…","en":"…"},
  "task":   { …task… }                   // EITHER a single task
  "levels": {"easy":{…task…}, "moderate":{…task…}, "hard":{…task…}}   // OR three levelled tasks (omit "task")
}
```
Use `levels` wherever it makes sense (most exercises and many activities). **moderate = the book's activity as printed** (same questions, same options). **easy** = same core idea with more support (fewer options — usually 2, picture/symbol support, shorter wording, fewer items). **hard** = a stretch (extra questions, no word bank → more distractors, "why?" reasoning, compare, apply to own life). If levelling adds nothing (e.g. "draw the flag"), use a single `task`.
If the book's activity is hands-on/class-based (collect pictures, group discussion, trace and cut a map, role play), keep it as an `open` task with clear `steps`, AND where sensible add a small on-screen interactive that practises the same idea (e.g. as the `easy` level, or as a second activity block with label "آزمائیں / Try it").
Where an exercise's answer has to be found on an earlier page of the chapter, that is fine — answers must be correct according to the book.

### Task kinds
```json
{"kind":"mcq", "questions":[
  {"q":{"ur":"پاکستان کب وجود میں آیا؟","en":"When did Pakistan come into being?"},
   "img":[x0,y0,x1,y1],                                   // optional picture for the question
   "options":[{"ur":"23 مارچ 1940ء","en":"23 March 1940"}, {"ur":"14 اگست 1947ء","en":"14 August 1947"}, {"ur":"11 ستمبر 1948ء","en":"11 September 1948"}],
   "answer":1,                                            // index of the correct option
   "fb":{"ur":"پاکستان 14 اگست 1947ء کو وجود میں آیا۔","en":"Pakistan came into being on 14 August 1947."}}   // short explanation shown after answering
]}
{"kind":"tf", "questions":[ {"q":{…statement…}, "answer":true, "fb":{…}} ]}          // درست / غلط
{"kind":"fill", "questions":[ {"q":{"ur":"پاکستان کا دارالحکومت ___ ہے۔","en":"The capital of Pakistan is ___."}, "options":[{…},{…},{…}], "answer":0, "fb":{…}} ]}   // exactly one ___ in q.ur and q.en; child picks the word
{"kind":"match", "pairs":[ {"a":{"ur":"سندھ","en":"Sindh"}, "b":{"ur":"کراچی","en":"Karachi"}} ]}     // 3–6 pairs; a and b may each carry "img":[crop] or "sym":"keyword"
{"kind":"sort", "groups":[{"ur":"دیہات","en":"Village"},{"ur":"شہر","en":"City"}], "items":[ {"ur":"کچے گھر","en":"Mud houses","group":0} ]}   // 2–3 groups, 4–8 items; items may carry "img" or "sym"
{"kind":"order", "items":[ {"ur":"…","en":"…"} ]}                                    // 3–5 items listed in the CORRECT order (app shuffles)
{"kind":"open", "mode":"write",                                                      // write | draw | talk | do
  "steps":[{"ur":"…","en":"…"}],                                                     // optional: 2–5 short steps
  "model":{"ur":"…","en":"…"},                                                       // optional: a sample good answer (shown on "show answer")
  "checklist":[{"ur":"…","en":"…"}]}                                                 // optional: 2–4 "I did …" self-check items
```
Options/items may carry `"sym":"english keyword"` (an ARASAAC pictogram is fetched for it — use simple concrete nouns/verbs like "water", "house", "farmer", "tree", "to help") or `"img":[crop]` (a crop from THIS page). Use these generously on `easy` levels.
For each mcq/tf/fill question vary the position of the correct answer. Keep feedback (`fb`) kind and explanatory — it is shown for both right and wrong answers.

## hint — the "Helpful hint" button (2–4 items)
```json
"hint":[
  {"for":"all",     "ur":"…", "en":"…"},     // a tip any learner can use on THIS page (what to look at first, a memory trick, a link to their own life)
  {"for":"vision",  "ur":"…", "en":"…"},     // for: all | vision | hearing | motor | cognitive | teacher
  {"for":"teacher", "ur":"…", "en":"…"}      // how an adult can include every child in this page's learning/activity
]
```
Hints must be specific to this page's content (not generic), practical, and respectful. Cover at least two different audiences per page. Examples: tactile alternatives (trace a raised map with glue/string), offering pointing/speaking instead of writing, pairing with a buddy, using real objects, sign/gesture for key words, breaking the task into steps, extra time, accepting drawing or oral answers.

## easy — the Easy Read version (learning scaffold for learners with intellectual disabilities)
Teach the 1 core idea of the page (max 2) with very short sentences and symbols.
```json
"easy": {
  "title": {"ur":"پاکستان","en":"Pakistan"},
  "image": {"crop":[…], "alt":{"ur":"…","en":"…"}},        // ONE big, clear picture from this page (or null if the page has none)
  "sentences": [                                          // 3–5 sentences, each 3–7 words, one idea each, simple present tense
    {"en":"Pakistan is our country.",
     "words":[{"ur":"پاکستان","sym":"Pakistan"},{"ur":"ہمارا","sym":"our"},{"ur":"ملک","sym":"country"},{"ur":"ہے۔","sym":null}]}
  ],
  "activity": {                                           // ONE very simple task on the core idea; same task kinds, no levels
    "prompt":{"ur":"…","en":"…"},
    "task":{"kind":"mcq","questions":[{"q":{…},"options":[{"ur":"…","en":"…","sym":"…"},{"ur":"…","en":"…","sym":"…"}],"answer":0,"fb":{…}}]}
  }
}
```
- `words`: the sentence split into words/short phrases in order (joined with spaces they form the Urdu sentence). `sym` = an English keyword for an ARASAAC pictogram that shows that word's meaning (concrete, common: "country", "flag", "green", "white", "water", "to drink", "tree", "farmer", "city", "village", "mosque", "to help", "happy", "four", "big"). Use `null` for small function words (ہے، کا، کی، کے، میں، اور، کو …). Give a symbol to every content word you can. Punctuation stays attached to the word.
- A word may use `"img":[crop]` instead of `sym` when a picture from this page is the best symbol (e.g. the Pakistan flag).
- Easy activity: usually an mcq with 1–2 questions and exactly 2 options, each with a `sym` or `img`; or a 2-group `sort` with 4 items; or a 3-pair `match`.
- For exercise pages, the easy version revises the chapter's core idea.

## Front/back matter
- cover (p001), back cover (p096), title page, credits, table of contents: `kind` cover/front/toc/back, `easy`: null, `print`: false, still give `title`, `blocks` (verbatim text; for the TOC use a `table` with columns number / chapter title / page) and 1–2 `hint` items.

## How to check your work (required)
Run from the project root:
```
.venv/bin/python tools/validate.py content/pNNN.json [more files…]
```
It validates the schema and writes `qa/crops/pNNN_sheet.jpg` — a contact sheet of every crop on the page, labelled. READ each sheet and fix any crop that cuts off the picture or includes text/decoration, then re-run until it prints `OK` for every file and the crops look right.
