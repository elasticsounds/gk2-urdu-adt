# English edition brief

`content/pNNN.json` holds one page of a Pakistani Class 2 (age ~7) General Knowledge textbook, written in Urdu, already adapted into an accessible digital textbook. Read `tools/SCHEMA.md` for the file format. Every text object is `{"ur": "...", "en": "..."}`. Until now `en` was only a rough reviewer translation. We are now publishing an **English edition** in which `en` is what the child reads on screen and hears read aloud by a text-to-speech voice. Your job is to make the English of your pages publishable, and to add English word-symbol rows to the Easy Read sentences.

## What to do for each of your pages
1. Read the whole file. Improve every `en` string so that it is:
   - a faithful translation of the `ur` beside it (same facts, same meaning, nothing added or dropped; book body text stays complete, not summarised);
   - natural, warm, simple English a 7-year-old understands, in British/Pakistani spelling (colour, neighbour, programme);
   - good when read aloud: full sentences, no translator notes, no bracketed glosses such as "(lit. …)", no transliterated Urdu where an English word exists. Drop bracket glosses that only made sense in Urdu, e.g. `برِاعظم (Continent)` → "continent".
   - consistent: Pakistan, Punjab, Sindh, Balochistan, Khyber Pakhtunkhwa, Gilgit-Baltistan, Azad Jammu and Kashmir, Islamabad, Quaid-e-Azam Muhammad Ali Jinnah, Allama Muhammad Iqbal, Minar-e-Pakistan, Eid-ul-Fitr, Eid-ul-Adha, mosque, Hazrat Muhammad (peace be upon him) — write honorifics out in words, e.g. "(peace be upon him)", "(may Allah be pleased with him)". Labels: "Activity", "Exercise", "Question 1", "Try it", "Do you know?", "For teachers".
   - `alt` text: one clear English sentence describing the picture.
   Many strings are already fine — leave good ones alone. Do not touch any `ur`, `crop`, `img`, `sym`, `answer`, `group`, ids or structure.
2. Activities must work in English. Check each task as an English-only child would see it:
   - `fill`: `q.en` has exactly one `___`, and the correct option's `en` fits the gap grammatically.
   - mcq/tf/match/sort/order: the English options are distinct, the keyed answer is still right in English, feedback explains the answer.
   - If a task depends on Urdu letters, spelling or word order and cannot work in English, rewrite only its `en` strings so it practises the same idea in English (keep the same number of options/items and the same answer index); mention it in your report.
3. Easy Read: every object in `easy.sentences` has `en` (the sentence) and `words` (Urdu word chips). Make `en` a very short, simple-present sentence (3–8 words, one idea) that says what the Urdu says, then **add `words_en`**: the English sentence split into words/short phrases in order, each `{"en": "...", "sym": "keyword"}` (or `"sym": null`, or `"img": [crop]`).
   - Joined with single spaces, the `words_en[].en` values must equal `en` exactly (punctuation stays attached to a word).
   - `sym` is an English keyword for an ARASAAC pictogram. Reuse the `sym`/`img` values from the Urdu `words` for the matching English word wherever you can (copy `img` crops exactly). Give a symbol to every content word; use `null` for small function words (is, the, a, of, in, and, to, are …). Group a phrase into one chip when it is one idea ("Pakistan Day", "is in", "our country").
   - Example: `"en": "Pakistan is our country.", "words_en": [{"en":"Pakistan","sym":"Pakistan"},{"en":"is","sym":null},{"en":"our","sym":"our"},{"en":"country.","sym":"country"}]`
   Also polish `easy.title.en` and the easy activity's `en` strings.
4. Edit the files in place with targeted edits (do not regenerate whole files; never change Urdu). Keep valid JSON.
5. Check, from the project root, and fix until every file prints OK for both:
   ```
   .venv/bin/python tools/validate_en.py content/pNNN.json …
   .venv/bin/python tools/validate.py content/pNNN.json …
   ```
   (`validate.py` also rewrites crop sheets in qa/crops — ignore those.)

## Report back (short)
List: pages done; any task you had to adapt for English and how; any place where the Urdu and the old English disagreed on a fact or an answer key looked wrong (page, id, what) — fix the English to match the Urdu and flag it; do not change answer keys.
