#!/usr/bin/env python3
"""Validate content/pNNN.json files against the ADT schema and write crop contact sheets."""
import json, sys, os, re
from PIL import Image, ImageDraw, ImageFont

KINDS = {"cover", "front", "toc", "opener", "content", "exercise", "back"}
TASKS = {"mcq", "tf", "fill", "match", "sort", "order", "open"}
BAD_CHARS = {"ي": "Arabic yeh ي (use ی)", "ك": "Arabic kaf ك (use ک)", "ى": "alef maksura ى (use ی)"}


def walk_crops(obj, path, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("crop", "img") and isinstance(v, list) and len(v) == 4 and all(isinstance(x, (int, float)) for x in v):
                out.append((path + "." + k, v))
            else:
                walk_crops(v, path + "." + k, out)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            walk_crops(v, f"{path}[{i}]", out)


def check(fn):
    errs = []
    E = errs.append
    try:
        d = json.load(open(fn, encoding="utf-8"))
    except Exception as ex:
        return [f"invalid JSON: {ex}"], None, []
    raw = open(fn, encoding="utf-8").read()
    for ch, msg in BAD_CHARS.items():
        if ch in raw:
            E(f"contains {msg} x{raw.count(ch)}")

    def txt(o, where, need_en=True):
        if not isinstance(o, dict) or not isinstance(o.get("ur"), str) or not o["ur"].strip():
            E(f"{where}: needs non-empty 'ur'")
            return
        if need_en and (not isinstance(o.get("en"), str) or not o["en"].strip()):
            E(f"{where}: needs non-empty 'en'")

    def crop(c, where):
        if not (isinstance(c, list) and len(c) == 4 and all(isinstance(x, (int, float)) for x in c)):
            E(f"{where}: crop must be [x0,y0,x1,y1]"); return
        x0, y0, x1, y1 = c
        if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
            E(f"{where}: crop out of range/order {c}")
        elif (x1 - x0) < 0.04 or (y1 - y0) < 0.03:
            E(f"{where}: crop too small {c}")

    def opt(o, where):
        txt(o, where)
        if "img" in o: crop(o["img"], where + ".img")
        if "sym" in o and o["sym"] is not None and not isinstance(o["sym"], str): E(f"{where}: sym must be string")

    def task(t, where):
        if not isinstance(t, dict) or t.get("kind") not in TASKS:
            E(f"{where}: task.kind must be one of {sorted(TASKS)}"); return
        k = t["kind"]
        if k in ("mcq", "fill", "tf"):
            qs = t.get("questions")
            if not isinstance(qs, list) or not qs: E(f"{where}: needs questions[]"); return
            for i, q in enumerate(qs):
                w = f"{where}.q{i}"
                txt(q.get("q"), w + ".q"); txt(q.get("fb"), w + ".fb")
                if "img" in q: crop(q["img"], w + ".img")
                if k == "tf":
                    if not isinstance(q.get("answer"), bool): E(f"{w}: tf answer must be true/false")
                else:
                    o = q.get("options")
                    if not isinstance(o, list) or len(o) < 2: E(f"{w}: needs >=2 options"); continue
                    for j, x in enumerate(o): opt(x, f"{w}.opt{j}")
                    a = q.get("answer")
                    if not isinstance(a, int) or isinstance(a, bool) or not (0 <= a < len(o)): E(f"{w}: answer index invalid")
                    if k == "fill":
                        for lang in ("ur", "en"):
                            if isinstance(q.get("q"), dict) and q["q"].get(lang, "").count("___") != 1:
                                E(f"{w}: fill q.{lang} must contain exactly one ___")
        elif k == "match":
            ps = t.get("pairs")
            if not isinstance(ps, list) or not (2 <= len(ps) <= 7): E(f"{where}: match needs 2-7 pairs"); return
            for i, p in enumerate(ps):
                opt(p.get("a", {}), f"{where}.pair{i}.a"); opt(p.get("b", {}), f"{where}.pair{i}.b")
        elif k == "sort":
            g = t.get("groups"); it = t.get("items")
            if not isinstance(g, list) or not (2 <= len(g) <= 4): E(f"{where}: sort needs 2-4 groups"); return
            for i, x in enumerate(g): opt(x, f"{where}.group{i}")
            if not isinstance(it, list) or len(it) < 2: E(f"{where}: sort needs items"); return
            for i, x in enumerate(it):
                opt(x, f"{where}.item{i}")
                if not isinstance(x.get("group"), int) or not (0 <= x["group"] < len(g)): E(f"{where}.item{i}: bad group index")
        elif k == "order":
            it = t.get("items")
            if not isinstance(it, list) or not (3 <= len(it) <= 6): E(f"{where}: order needs 3-6 items"); return
            for i, x in enumerate(it): opt(x, f"{where}.item{i}")
        elif k == "open":
            if t.get("mode") not in ("write", "draw", "talk", "do"): E(f"{where}: open.mode must be write|draw|talk|do")
            for i, x in enumerate(t.get("steps", []) or []): txt(x, f"{where}.step{i}")
            if t.get("model") is not None: txt(t["model"], f"{where}.model")
            for i, x in enumerate(t.get("checklist", []) or []): txt(x, f"{where}.check{i}")

    def activity(a, where, full=True):
        txt(a.get("prompt"), where + ".prompt")
        if full:
            if not re.fullmatch(r"p\d{3}-a\d+", str(a.get("id", ""))): E(f"{where}: id must look like p013-a1")
            txt(a.get("label"), where + ".label"); txt(a.get("orig"), where + ".orig")
        if "levels" in a:
            lv = a["levels"]
            if not isinstance(lv, dict) or set(lv) != {"easy", "moderate", "hard"}: E(f"{where}: levels must have easy, moderate, hard"); return
            if "task" in a: E(f"{where}: give task OR levels, not both")
            for k2, t in lv.items(): task(t, f"{where}.{k2}")
        elif "task" in a:
            task(a["task"], where + ".task")
        else:
            E(f"{where}: needs task or levels")

    n = d.get("n")
    m = re.search(r"p(\d{3})\.json$", fn)
    if not isinstance(n, int) or not m or int(m.group(1)) != n: E("'n' must equal the page number in the filename")
    if d.get("kind") not in KINDS: E(f"kind must be one of {sorted(KINDS)}")
    if not isinstance(d.get("printed"), str): E("printed must be a string")
    if not isinstance(d.get("chapter"), int): E("chapter must be int")
    if not isinstance(d.get("print"), bool): E("print must be true/false")
    txt(d.get("title"), "title")
    ids = set()
    bl = d.get("blocks")
    if not isinstance(bl, list) or not bl: E("blocks[] required")
    else:
        for i, b in enumerate(bl):
            w = f"blocks[{i}]"; t = b.get("t") if isinstance(b, dict) else None
            if t in ("h", "p", "fact", "teacher", "note"): txt(b, w)
            elif t == "list":
                if not b.get("items"): E(f"{w}: list needs items")
                for j, x in enumerate(b.get("items", [])): txt(x, f"{w}.items[{j}]")
            elif t == "img":
                crop(b.get("crop"), w); txt(b.get("alt"), w + ".alt")
                if "cap" in b: txt(b["cap"], w + ".cap")
            elif t == "gallery":
                if not isinstance(b.get("items"), list) or len(b["items"]) < 2: E(f"{w}: gallery needs 2+ items")
                for j, x in enumerate(b.get("items", [])):
                    crop(x.get("crop"), f"{w}.items[{j}]"); txt(x.get("alt"), f"{w}.items[{j}].alt")
                    if "cap" in x: txt(x["cap"], f"{w}.items[{j}].cap")
            elif t == "table":
                for j, x in enumerate(b.get("head", [])): txt(x, f"{w}.head[{j}]")
                if not b.get("rows"): E(f"{w}: table needs rows")
                for r, row in enumerate(b.get("rows", [])):
                    for j, x in enumerate(row):
                        if not isinstance(x, dict) or not isinstance(x.get("ur"), str): E(f"{w}.rows[{r}][{j}]: needs ur")
            elif t == "activity":
                activity(b, w)
                if b.get("id") in ids: E(f"{w}: duplicate id")
                ids.add(b.get("id"))
            else:
                E(f"{w}: unknown block type {t!r}")
    h = d.get("hint")
    if not isinstance(h, list) or not (1 <= len(h) <= 5): E("hint must have 1-5 items")
    else:
        for i, x in enumerate(h):
            txt(x, f"hint[{i}]")
            if x.get("for") not in ("all", "vision", "hearing", "motor", "cognitive", "teacher"): E(f"hint[{i}].for invalid")
    e = d.get("easy", "MISSING")
    if e == "MISSING": E("'easy' key required (object or null)")
    elif e is None:
        if d.get("kind") in ("opener", "content", "exercise"): E("easy is required for opener/content/exercise pages")
    else:
        txt(e.get("title"), "easy.title")
        im = e.get("image")
        if im is not None:
            crop(im.get("crop"), "easy.image"); txt(im.get("alt"), "easy.image.alt")
        s = e.get("sentences")
        if not isinstance(s, list) or not (2 <= len(s) <= 6): E("easy.sentences: 2-6 sentences")
        else:
            for i, x in enumerate(s):
                if not isinstance(x.get("en"), str): E(f"easy.sentences[{i}]: needs en")
                ws = x.get("words")
                if not isinstance(ws, list) or not (2 <= len(ws) <= 9): E(f"easy.sentences[{i}]: 2-9 words"); continue
                nsym = 0
                for j, wd in enumerate(ws):
                    if not isinstance(wd.get("ur"), str) or not wd["ur"].strip(): E(f"easy.sentences[{i}].words[{j}]: needs ur")
                    if wd.get("sym") or wd.get("img"): nsym += 1
                    if "img" in wd: crop(wd["img"], f"easy.sentences[{i}].words[{j}].img")
                if nsym == 0: E(f"easy.sentences[{i}]: give at least one word a sym")
        a = e.get("activity")
        if not isinstance(a, dict): E("easy.activity required")
        else: activity(a, "easy.activity", full=False)
    crops = []
    walk_crops(d, "", crops)
    return errs, d, crops


def sheet(n, crops):
    src = f"adt/assets/pages/p{n:03d}.jpg"
    if not crops or not os.path.exists(src): return
    im = Image.open(src).convert("RGB"); W, H = im.size
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 13)
    cells = []
    for path, c in crops:
        try:
            x0, y0, x1, y1 = c
            cr = im.crop((int(x0 * W), int(y0 * H), int(x1 * W), int(y1 * H)))
        except Exception:
            continue
        s = min(300 / cr.width, 230 / cr.height, 3)
        cr = cr.resize((max(1, int(cr.width * s)), max(1, int(cr.height * s))))
        cells.append((path, c, cr))
    cols = 4; cw, ch = 320, 280
    rows = (len(cells) + cols - 1) // cols
    S = Image.new("RGB", (cols * cw, rows * ch), (40, 40, 40)); dr = ImageDraw.Draw(S)
    for k, (path, c, cr) in enumerate(cells):
        x, y = (k % cols) * cw, (k // cols) * ch
        S.paste(cr, (x + 10, y + 36))
        dr.text((x + 6, y + 3), path[-44:], fill="white", font=font)
        dr.text((x + 6, y + 18), str(c), fill=(160, 220, 255), font=font)
    os.makedirs("qa/crops", exist_ok=True)
    S.save(f"qa/crops/p{n:03d}_sheet.jpg", quality=85)


if __name__ == "__main__":
    bad = 0
    for fn in sys.argv[1:]:
        errs, d, crops = check(fn)
        if d is not None and isinstance(d.get("n"), int): sheet(d["n"], crops)
        if errs:
            bad += 1
            print(f"{fn}: {len(errs)} problem(s)")
            for e in errs[:40]: print("   -", e)
        else:
            print(f"{fn}: OK ({len(crops)} crops -> qa/crops/p{d['n']:03d}_sheet.jpg)")
    sys.exit(1 if bad else 0)
