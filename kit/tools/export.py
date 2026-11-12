#!/usr/bin/env python3
"""Braille (BRF) and text-only HTML exports of every page, for both editions.

    python tools/export.py          -> adt/exports/{ur,en}/pNNN.brf, pNNN.html, book.brf, book.html

BRF: 40 cells x 25 lines, form feed between braille pages, uncontracted braille.
  Urdu edition: liblouis ur-pk-g1 (Latin letters and symbols the Urdu table lacks go through UEB grade 1).
  English edition: liblouis en-ueb-g1 (Unified English Braille, uncontracted).
Needs liblouis (`brew install liblouis`) for the `lou_translate` command.
"""
import glob, html, json, os, re, subprocess, sys, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
CELLS, LINES = 40, 25
ASCII = " A1B'K2L@CIF/MSP\"E3H9O6R^DJG>NTQ,*5<-U8V.%[$+X!&;:4\\0Z7(_?W]#Y)="   # braille ASCII, indexed by dot pattern
S = {
    "ur": dict(book="واقفیتِ عامہ", klass="جماعت دوم", page="صفحہ", of="از", printed="کتاب کا صفحہ", picture="تصویر", caption="عنوان",
               fact="کیا آپ جانتے ہیں؟", teacher="برائے اساتذہ", note="نوٹ", answers="جوابات", hints="مددگار اشارے", true="درست", false="غلط",
               choose="ان میں سے چنیں", match="ملائیں", colA="پہلی فہرست", colB="دوسری فہرست", groups="گروہ", items="چیزیں", order="صحیح ترتیب میں لگائیں",
               sample="نمونہ جواب", contents="فہرست", about="یہ صرف متن والا نسخہ ہے۔ تصویروں کی جگہ ان کی تفصیل لکھی گئی ہے۔", activity="سرگرمی",
               letters=["الف", "ب", "ج", "د", "ہ", "و", "ز", "ح"], who=dict(all="سب کے لیے", vision="نظر", hearing="سماعت", motor="حرکت", cognitive="سمجھ", teacher="اساتذہ کے لیے")),
    "en": dict(book="General Knowledge", klass="Class 2", page="Page", of="of", printed="book page", picture="Picture", caption="Caption",
               fact="Do you know?", teacher="For teachers", note="Note", answers="Answers", hints="Helpful hints", true="True", false="False",
               choose="Choose from", match="Match", colA="First list", colB="Second list", groups="Groups", items="Items", order="Put these in the right order",
               sample="Sample answer", contents="Contents", about="This is a text-only version. Pictures are replaced by their descriptions.", activity="Activity",
               letters=list("abcdefgh"), who=dict(all="For everyone", vision="Vision", hearing="Hearing", motor="Movement", cognitive="Understanding", teacher="For teachers")),
}


# ---------- page -> list of (kind, text); kinds: h1 h2 h3 p li ----------
def items_for(d, L):
    s = S[L]; T = lambda o: (o or {}).get(L, "").strip()
    out = [("h1", T(d["title"]))]
    out.append(("p", f"{s['book']}, {s['klass']}. {s['page']} {d['n']} {s['of']} 96" + (f" ({s['printed']} {d['printed']})" if d.get("printed") else "") + "."))
    answers = []

    def pic(b):
        if T(b.get("alt")): out.append(("p", f"{s['picture']}: {T(b['alt'])}"))
        if T(b.get("cap")): out.append(("p", f"{s['caption']}: {T(b['cap'])}"))

    def task(t, label):
        k = t["kind"]; ans = []
        if k in ("mcq", "fill"):
            for i, q in enumerate(t["questions"], 1):
                out.append(("p", f"{i}. {T(q['q'])}"))
                for j, o in enumerate(q["options"]): out.append(("li", f"{s['letters'][j]}) {T(o)}"))
                ans.append(f"{i}. {s['letters'][q['answer']]}) {T(q['options'][q['answer']])}")
        elif k == "tf":
            for i, q in enumerate(t["questions"], 1):
                out.append(("li", f"{i}. {T(q['q'])} ({s['true']} / {s['false']})"))
                ans.append(f"{i}. {s['true'] if q['answer'] else s['false']}")
        elif k == "match":
            out.append(("p", f"{s['colA']}:"))
            for i, p in enumerate(t["pairs"], 1): out.append(("li", f"{i}. {T(p['a'])}"))
            out.append(("p", f"{s['colB']}:"))
            for x in sorted(T(p["b"]) for p in t["pairs"]): out.append(("li", x))
            ans += [f"{i}. {T(p['a'])}: {T(p['b'])}" for i, p in enumerate(t["pairs"], 1)]
        elif k == "sort":
            out.append(("p", f"{s['groups']}: " + "; ".join(T(g) for g in t["groups"]) + "."))
            out.append(("p", f"{s['items']}:"))
            for x in sorted(T(i) for i in t["items"]): out.append(("li", x))
            for gi, g in enumerate(t["groups"]): ans.append(f"{T(g)}: " + "; ".join(T(i) for i in t["items"] if i["group"] == gi))
        elif k == "order":
            out.append(("p", f"{s['order']}:"))
            for x in sorted(T(i) for i in t["items"]): out.append(("li", x))
            ans += [f"{i}. {T(x)}" for i, x in enumerate(t["items"], 1)]
        elif k == "open":
            for i, x in enumerate(t.get("steps") or [], 1): out.append(("li", f"{i}. {T(x)}"))
            if T(t.get("model")): ans.append(f"{s['sample']}: {T(t['model'])}")
        if ans: answers.append((label, ans))

    for b in d["blocks"]:
        t = b["t"]
        if t == "h": out.append(("h2", T(b)))
        elif t == "p": out.append(("p", T(b)))
        elif t in ("fact", "teacher", "note"): out.append(("p", f"{s[t]} {T(b)}" if t == "fact" else f"{s[t]}: {T(b)}"))
        elif t == "list": out += [("li", T(i)) for i in b["items"]]
        elif t == "table":
            if b.get("head") and any(T(c) for c in b["head"]): out.append(("p", "; ".join(T(c) for c in b["head"] if T(c)) + ":"))
            out += [("li", "; ".join(T(c) for c in r if T(c))) for r in b["rows"]]
        elif t == "img": pic(b)
        elif t == "gallery":
            for i in b["items"]: pic(i)
        elif t == "activity":
            label = T(b.get("label")) or s["activity"]
            out.append(("h2", label))
            tk = b.get("task") or b["levels"]["moderate"]
            out.append(("p", T(b["orig"]) if tk["kind"] == "open" and T(b.get("orig")) else T(b.get("prompt")) or T(b.get("orig"))))
            task(tk, label)
    if d.get("hint"):
        out.append(("h2", s["hints"]))
        out += [("li", f"{s['who'].get(x.get('for'), s['who']['all'])}: {T(x)}") for x in d["hint"]]
    if answers:
        out.append(("h2", s["answers"]))
        for label, ans in answers:
            out.append(("h3", label)); out += [("li", a) for a in ans]
    return [(k, re.sub(r"\s+", " ", x)) for k, x in out if x]


# ---------- braille ----------
CLEAN = {"ﷺ": " صلی اللہ علیہ وسلم", "✓": "", "✗": "", "←": " ", "→": " ", "•": "", "…": "...", "ٖ": "", "‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-", "٪": "%", "|": " ", "‌": "", "‍": "", "‎": "", "‏": ""}


def louis(table, lines):
    r = subprocess.run(["lou_translate", "unicode.dis," + table], input="\n".join(lines) + "\n", capture_output=True, text=True, check=True)
    out = r.stdout.split("\n")[:len(lines)]
    assert len(out) == len(lines), (len(out), len(lines))
    return out


def bad(cell_text):
    return any(ord(c) > 0x283F for c in cell_text)   # dots 7/8 only appear in liblouis's "undefined character" escapes


def make_translator(L, corpus):
    if L == "en":
        return lambda lines: louis("en-ueb-g1.ctb", lines)
    chars = sorted({c for t in corpus for ch in t for c in CLEAN.get(ch, ch) if not c.isspace()} | set("_"))
    mark = lambda c: unicodedata.category(c) == "Mn"
    probe = louis("ur-pk-g1.utb", [("ب" if mark(c) else "ب ") + c + " ب" for c in chars])
    drop = {c for c, o in zip(chars, probe) if bad(o) and mark(c)}       # vowel marks the Urdu table has no sign for
    latin = {c for c, o in zip(chars, probe) if bad(o) and not mark(c)}   # what the Urdu table cannot write: sent through UEB instead

    def tr(lines):
        runs, plan = [], []
        for ln in lines:
            parts = []; cur = ""; cur_lat = None
            for c in (x for x in ln if x not in drop):
                lat = cur_lat if c.isspace() else (c in latin)
                if cur and lat != cur_lat: parts.append((cur_lat, cur)); cur = ""
                cur += c; cur_lat = lat if lat is not None else False
            if cur: parts.append((cur_lat, cur))
            plan.append(parts)
        ur = [p for parts in plan for lat, p in parts if not lat]; en = [p for parts in plan for lat, p in parts if lat]
        ur_o = iter(louis("ur-pk-g1.utb", [p.strip() for p in ur]) if ur else []); en_o = iter(louis("en-ueb-g1.ctb", [p.strip() for p in en]) if en else [])
        out = []
        for parts in plan:
            s = ""
            for lat, p in parts:
                b = next(en_o if lat else ur_o)
                s += ("⠀" if p[:1].isspace() else "") + b + ("⠀" if p[-1:].isspace() and p.strip() else "")
            out.append(re.sub("⠀+", "⠀", s).strip("⠀"))
        return out
    return tr


UNKNOWN = []


def to_ascii(u):
    UNKNOWN.extend(c for c in u if not (c == " " or 0x2800 <= ord(c) <= 0x283F))
    return "".join(" " if c in " ⠀" else ASCII[ord(c) - 0x2800] if 0x2800 < ord(c) <= 0x283F else "" for c in u)


def wrap(text, first, rest):
    lines = []; cur = " " * first
    for w in text.split():
        while len(w) > CELLS - rest:   # a word longer than a line
            room = CELLS - len(cur) - (1 if cur.strip() else 0)
            if room < 8: lines.append(cur.rstrip()); cur = " " * rest; continue
            cur += (" " if cur.strip() else "") + w[:room]; w = w[room:]; lines.append(cur); cur = " " * rest
        if len(cur) + (1 if cur.strip() else 0) + len(w) > CELLS: lines.append(cur.rstrip()); cur = " " * rest
        cur += (" " if cur.strip() else "") + w
    if cur.strip(): lines.append(cur.rstrip())
    return lines


def brf(items, tr):
    cells = [to_ascii(b) for b in tr([re.sub(r"[_\u0640]{2,}", "____", x).replace("\u0640", "").translate(str.maketrans({k: v for k, v in CLEAN.items()})) for _, x in items])]
    lines = []
    for (k, _), c in zip(items, cells):
        if not c.strip(): continue
        if k == "h1": lines += [x.strip().center(CELLS).rstrip() for x in wrap(c, 0, 0)] + [""]
        elif k == "h2": lines += ([""] if lines and lines[-1] else []) + [x.strip().center(CELLS).rstrip() for x in wrap(c, 0, 0)] + [""]
        elif k == "h3": lines += ([""] if lines and lines[-1] else []) + wrap(c, 4, 4)
        elif k == "p": lines += wrap(c, 2, 0)
        else: lines += wrap(c, 0, 2)
    pages = [lines[i:i + LINES] for i in range(0, len(lines), LINES)]
    pages = [p[1:] if p and not p[0] else p for p in pages]   # no blank line at the top of a braille page
    return "\f".join("\r\n".join(p) + "\r\n" for p in pages)


# ---------- text-only HTML ----------
CSS = "body{max-width:42rem;margin:1rem auto;padding:0 1rem;font:1.15rem/1.9 'Noto Nastaliq Urdu','Jameel Noori Nastaleeq',system-ui,sans-serif;color:#111;background:#fff}h1,h2,h3{line-height:1.6}ul{list-style:none;padding-inline-start:1.2rem}a{color:#00429d}@media(prefers-color-scheme:dark){body{color:#eee;background:#111}a{color:#9cc4ff}}"


def body_html(items, shift=0):
    o = []; in_ul = False
    for k, x in items:
        if k == "li":
            if not in_ul: o.append("<ul>"); in_ul = True
            o.append(f"<li>{html.escape(x)}</li>"); continue
        if in_ul: o.append("</ul>"); in_ul = False
        tag = f"h{int(k[1]) + shift}" if k[0] == "h" else "p"
        o.append(f"<{tag}>{html.escape(x)}</{tag}>")
    if in_ul: o.append("</ul>")
    return "\n".join(o)


def page_html(L, title, inner):
    d = "rtl" if L == "ur" else "ltr"
    return (f'<!doctype html>\n<html lang="{L}" dir="{d}">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            f'<meta name="robots" content="noindex">\n<title>{html.escape(title)}</title>\n<style>{CSS}</style>\n</head>\n<body>\n<main>\n{inner}\n</main>\n</body>\n</html>\n')


def main():
    pages = [json.load(open(f, encoding="utf-8")) for f in sorted(glob.glob("content/p*.json"))]
    for L in ("ur", "en"):
        s = S[L]; out = f"adt/exports/{L}"; os.makedirs(out, exist_ok=True)
        its = [items_for(d, L) for d in pages]
        tr = make_translator(L, [x for it in its for _, x in it])
        book_brf, book_html, toc = [], [], []; UNKNOWN.clear()
        for d, it in zip(pages, its):
            n = d["n"]; b = brf(it, tr)
            open(f"{out}/p{n:03d}.brf", "w", encoding="ascii", newline="").write(b)
            open(f"{out}/p{n:03d}.html", "w", encoding="utf-8").write(page_html(L, f"{it[0][1]} | {s['book']}, {s['page']} {n}", body_html(it) + f"\n<p><small>{html.escape(s['about'])}</small></p>"))
            book_brf.append(b)
            book_html.append(f'<section id="p{n}">\n{body_html(it, 1)}\n</section>')
            toc.append(f'<li><a href="#p{n}">{html.escape(s["page"])} {n}: {html.escape(it[0][1])}</a></li>')
        open(f"{out}/book.brf", "w", encoding="ascii", newline="").write("\f".join(book_brf))
        inner = f"<h1>{html.escape(s['book'])}, {html.escape(s['klass'])}</h1>\n<p>{html.escape(s['about'])}</p>\n<nav aria-label=\"{html.escape(s['contents'])}\">\n<h2>{html.escape(s['contents'])}</h2>\n<ol>\n" + "\n".join(toc) + "\n</ol>\n</nav>\n" + "\n".join(book_html)
        open(f"{out}/book.html", "w", encoding="utf-8").write(page_html(L, f"{s['book']}, {s['klass']}", inner))
        allb = "".join(book_brf); width = max(len(l) for l in allb.replace("\f", "\r\n").split("\r\n"))
        print(L, "pages", len(pages), "| braille pages", allb.count("\f") + len(pages), "| widest line", width, "| untranslatable cells", len(UNKNOWN), sorted(set(UNKNOWN))[:20],
              "| book.brf %d KB, book.html %d KB" % (len(allb) // 1024, os.path.getsize(f"{out}/book.html") // 1024))


if __name__ == "__main__":
    if subprocess.run(["which", "lou_translate"], capture_output=True).returncode: sys.exit("lou_translate not found: install liblouis (brew install liblouis)")
    main()
