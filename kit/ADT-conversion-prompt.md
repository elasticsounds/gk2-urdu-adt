# Prompt: convert a textbook PDF into an Accessible Digital Textbook

Fill in the block at the top, then paste the whole thing into a new Claude Code session.

---

## Fill in before use

- **PDF:** `<path to the PDF>`
- **Book:** `<title, subject, grade, publisher>`
- **Book language and script:** `<e.g. Urdu, Nastaliq, right-to-left>`
- **Second edition language (optional):** `<e.g. English, or "none">`
- **Reference build (optional):** `<path or GitHub repo of an earlier book made this way>`
- **Publish to:** `<GitHub repo name for GitHub Pages, or "local only">`
- **Keys available in my environment:** `REPLICATE_API_TOKEN` (upscaling). Symbol-library keys, if any, are in `<path>`.

---

## The job

Convert this PDF into an Accessible Digital Textbook: a web version of the whole book that a child can read, listen to and interact with on a phone, including children who are blind, have low vision, or find reading hard. Every page of the PDF becomes one page of the web book. Keep going until the whole book is done and checked; do not stop at a sample unless I ask for one.

If a reference build is given above, read it first and reuse its app, data format and build scripts. Change only what this book needs. If there is none, build the same thing from the description below.

## What every page must have

1. **The page's text, re-typed** as real text, split into short sentences, fitted to a phone screen with no sideways scrolling. Preserve the book's wording exactly in the main view.
2. **Read-aloud** for every sentence, with the word being spoken highlighted.
3. **The page's pictures**, cropped from the scan, each with a written description that is also read aloud.
4. **Interactive activities** for every exercise on the page, with correct answers, and spoken feedback for right and wrong attempts.
5. **A hint** button with one helpful hint for the page.
6. **Three levels:** easy, moderate and hard versions of the activities.
7. **An easy-read version:** the page's ideas in very short sentences, each word paired with a picture symbol, plus one easy-read activity.
8. **A switch to the original scanned page**, so a teacher can compare.
9. **Print.**

## How the reader app must behave

- Static site, no build step and no server: plain HTML, CSS and JavaScript, one data file per page, loaded on demand. It must work from GitHub Pages.
- Navigation: previous/next, a table of contents, and a direct link for every page.
- **Listening mode:** one Listen button. When it is on, the page reads itself aloud from the top, tapping any sentence jumps to it, and turning the page starts the new page automatically. No speaker icon beside each sentence. Do not turn pages automatically.
- **Pictures:** tapping a picture enlarges it with its description as a caption and reads the description aloud. A setting controls whether picture descriptions are included when a page is read.
- Settings for text size, theme (including high contrast), reading speed and interface language, remembered on the device.
- Works with keyboard and screen readers: real buttons, labels, focus order, dialogs that trap focus.
- Right-to-left layout and a suitable font when the book's script needs it.

## How to produce the content

Work page by page. For each page, look at the scanned page image yourself and write its content file: sentences, picture regions and descriptions, activities with answer keys, hint, levels, easy-read sentences. Use subagents to do ranges of pages in parallel, giving each one the written schema and two finished pages as examples. Keep the content files as the single source of truth and generate everything else from them.

- Remove watermarks from the page images before cropping pictures.
- Write a validator that checks every content file against the schema and run it after each batch.
- Answer keys must be justified by the book itself. Where the book is ambiguous, pick the answer the book's own text supports and list the item for my review.

## Voices

- Pre-generate every clip as an MP3 at build time, with word timings saved for highlighting. Name clips by a hash of voice, speed and text, so unchanged text is never regenerated.
- Use a neural voice native to the book's language and country, slowed about 10–12% for children. Tell me which voice you chose and whether it comes from a free unofficial source or a paid, licensed one.

## Symbols

- Look up easy-read symbols from ARASAAC first, then other open symbol libraries. Cache lookups, keep an override file for wrong matches, and record credits and licences.

## Pictures

Upscale the cropped pictures through Replicate, then cap them at 1800 px on the long side and save as JPEG:

- **Photographs, and any drawing with people or cartoon animals in it:** `philz1337x/crystal-upscaler`, scale 4, creativity 0.
- **Maps, diagrams, plants and objects:** `recraft-ai/recraft-crisp-upscale`.
- Do not use image-generation models for this. They redraw the picture and rewrite any lettering in it.
- Keep the originals. Check that every result has the same proportions as its source, and look at before-and-after sheets, with close-ups of faces and of any lettering inside pictures.

## Second-language edition (if requested)

Same app, same pictures, separate data and audio. Translate every field, including easy-read word lists and picture descriptions, and validate that no source-language text is left behind. Add a button to switch editions.

## Checks before you tell me it is done

- Every page loads with no console errors, in both editions.
- No sentence, hint, feedback line or picture description is missing its audio.
- Every activity can be completed and gives the right feedback at each level.
- Open at least ten pages in a real browser at phone width and try listening mode, a picture, an activity, the easy-read view and the original-page view.

## Rules

- Keep API keys out of the published folder, out of the repository and out of chat.
- Before spending on paid APIs for the whole book, run a small trial, show me the results large enough to judge, and tell me the cost.
- If publishing, use a GitHub Pages workflow, mark the site as not for search indexing, and confirm the live site matches the local build.

## What to report at the end

- The link, and what was and was not checked.
- Every answer key or translation you were unsure of, by page.
- What it cost.
- Licences that limit reuse: the symbol libraries, the voice source and the textbook itself.
