#!/usr/bin/env python3
"""Build the ADT data from content/pNNN.json.
   python tools/build.py            -> crops + data (uses cached symbols/audio only)
   python tools/build.py --sym      -> also fetch missing ARASAAC symbols
   python tools/build.py --tts      -> also synthesise missing audio (edge-tts, ur-PK)
"""
import json, glob, os, re, sys, hashlib, asyncio, copy, urllib.request, urllib.parse
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
OUT = "adt"
LANG = "en" if "--lang=en" in sys.argv else "ur"
VOICE = "en-IN-NeerjaNeural" if LANG == "en" else "ur-PK-UzmaNeural"
RATE = "-10%" if LANG == "en" else "-12%"
DATA = "data/en" if LANG == "en" else "data"
for d in ("assets/img", "assets/sym", "assets/audio", DATA):
    os.makedirs(f"{OUT}/{d}", exist_ok=True)
DO_SYM = "--sym" in sys.argv
DO_TTS = "--tts" in sys.argv

SYM_CACHE_F = "tools/sym_cache.json"
MARKS_F = "tools/audio_marks.json"
sym_cache = json.load(open(SYM_CACHE_F)) if os.path.exists(SYM_CACHE_F) else {}
marks = json.load(open(MARKS_F)) if os.path.exists(MARKS_F) else {}
SYM_OVERRIDE = json.load(open("tools/sym_override.json")) if os.path.exists("tools/sym_override.json") else {}

page_imgs = {}


def crop_src(n, c):
    key = hashlib.sha1(json.dumps([n, [round(x, 4) for x in c]]).encode()).hexdigest()[:10]
    fn = f"assets/img/p{n:03d}_{key}.jpg"
    path = f"{OUT}/{fn}"
    if n not in page_imgs:
        page_imgs[n] = Image.open(f"{OUT}/assets/pages/p{n:03d}.jpg").convert("RGB")
    im = page_imgs[n]; W, H = im.size
    box = (round(c[0] * W), round(c[1] * H), round(c[2] * W), round(c[3] * H))
    cr = im.crop(box)
    w, h = cr.size
    if not os.path.exists(path):
        s = 2 if max(w, h) < 900 else 1
        cr.resize((w * s, h * s), Image.LANCZOS).save(path, quality=86)
    return fn, w, h


def http_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "adt-builder"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode())


KEYS = json.load(open("tools/.keys.json")) if os.path.exists("tools/.keys.json") else {}
_os_tok = [None]
SYM_CREDITS_F = "tools/sym_credits.json"
sym_credits = json.load(open(SYM_CREDITS_F)) if os.path.exists(SYM_CREDITS_F) else {}


def _save_sym(url, name):
    ext = ".svg" if url.lower().split("?")[0].endswith(".svg") else ".png"
    fn = f"assets/sym/{name}{ext}"
    req = urllib.request.Request(url, headers={"User-Agent": "adt-builder"})
    with urllib.request.urlopen(req, timeout=30) as r, open(f"{OUT}/{fn}", "wb") as f:
        f.write(r.read())
    return fn


def fallback_symbol(k):
    """Words ARASAAC cannot match: try Global Symbols, then OpenSymbols."""
    slug = re.sub(r"[^a-z0-9]+", "-", k).strip("-")
    q = k[3:] if k.startswith("to ") else k
    if KEYS.get("globalsymbols_key"):
        try:
            req = urllib.request.Request("https://globalsymbols.com/api/v1/labels/search?" + urllib.parse.urlencode({"query": q, "language": "eng", "language_iso_format": "639-3", "limit": 20}),
                                         headers={"User-Agent": "adt-builder", "X-Api-Key": KEYS["globalsymbols_key"]})
            d = json.loads(urllib.request.urlopen(req, timeout=25).read().decode())
            pref = {17: 0, 13: 1, 205: 1, 86: 1, 81: 3, 15: 2, 14: 2}
            d = [x for x in d if x["picto"]["symbolset_id"] in pref and x["text"].strip().lower() in (q, k)]
            d.sort(key=lambda x: pref[x["picto"]["symbolset_id"]])
            if d:
                fn = _save_sym(d[0]["picto"]["image_url"], "gs-" + slug)
                sym_credits[fn] = "Global Symbols set %s" % d[0]["picto"]["symbolset_id"]
                json.dump(sym_credits, open(SYM_CREDITS_F, "w"), indent=0)
                return fn
        except Exception:
            pass
    if KEYS.get("opensymbols_secret"):
        try:
            if not _os_tok[0]:
                req = urllib.request.Request("https://www.opensymbols.org/api/v2/token", data=urllib.parse.urlencode({"secret": KEYS["opensymbols_secret"]}).encode(), headers={"User-Agent": "adt-builder"})
                _os_tok[0] = json.loads(urllib.request.urlopen(req, timeout=25).read().decode())["access_token"]
            d = http_json("https://www.opensymbols.org/api/v2/symbols?" + urllib.parse.urlencode({"q": q, "locale": "en", "access_token": _os_tok[0]}))
            order = {"arasaac": 0, "mulberry": 1, "tawasol": 2, "sclera": 3}
            d = [x for x in d if x.get("repo_key") in order]
            d.sort(key=lambda x: (order[x["repo_key"]], -(x.get("relevance") or 0)))
            if d:
                fn = _save_sym(d[0]["image_url"], "os-" + slug)
                sym_credits[fn] = "%s (%s) via OpenSymbols" % (d[0].get("repo_key"), d[0].get("license"))
                json.dump(sym_credits, open(SYM_CREDITS_F, "w"), indent=0)
                return fn
        except Exception:
            pass
    return None


def sym_src(kw):
    k = kw.strip().lower()
    if not k: return None
    if k in SYM_OVERRIDE:
        k = SYM_OVERRIDE[k]
        if k is None: return None
    if k in sym_cache:
        return sym_cache[k]
    if not DO_SYM:
        return None
    res = None
    cands = [k[3:], k] if k.startswith("to ") else [k]
    if " " in k: cands += [k.split(" ")[-1], k.split(" ")[0]]
    for q in cands:
        for ep in ("bestsearch", "search"):
            try:
                d = http_json(f"https://api.arasaac.org/api/pictograms/en/{ep}/{urllib.parse.quote(q)}")
                if isinstance(d, list) and d:
                    res = d[0]["_id"]; break
            except Exception:
                pass
        if res: break
    if not res:
        fb = fallback_symbol(k)
        if fb:
            sym_cache[k] = fb; return fb
    if res:
        fn = f"assets/sym/{res}.png"
        if not os.path.exists(f"{OUT}/{fn}"):
            try:
                req = urllib.request.Request(f"https://static.arasaac.org/pictograms/{res}/{res}_300.png", headers={"User-Agent": "adt-builder"})
                with urllib.request.urlopen(req, timeout=30) as r, open(f"{OUT}/{fn}", "wb") as f:
                    f.write(r.read())
            except Exception:
                fn = None
        sym_cache[k] = fn
    else:
        sym_cache[k] = None
        print("  no symbol for:", k)
    return sym_cache[k]


def speak_text(ur):
    if LANG == "en": ur = re.sub(r"_{4,}", " ", ur)
    t = ur.replace("___", ", blank, " if LANG == "en" else "، خالی جگہ، ")
    t = re.sub(r"[_]{2,}|[.]{3,}|…", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def aid(ur):
    return hashlib.sha1((VOICE + RATE + speak_text(ur)).encode("utf-8")).hexdigest()[:12]


need_audio = {}


def reg_audio(ur):
    if not ur or not re.search(r"[؀-ۿ0-9A-Za-z]", ur): return None
    i = aid(ur)
    need_audio[i] = ur
    return i


def localize(o):
    """English edition: English becomes the primary text (stored in "ur"), Urdu the secondary (stored in "en")."""
    if isinstance(o, list):
        for x in o: localize(x)
        return
    if not isinstance(o, dict): return
    if isinstance(o.get("words"), list):
        we = o.pop("words_en", None)
        if LANG == "en":
            ur_sentence = " ".join(w["ur"].strip() for w in o["words"])
            if we:
                o["words"] = [dict({k: v for k, v in w.items() if k != "en"}, ur=w["en"]) for w in we]
                o["ur"] = " ".join(w["ur"].strip() for w in o["words"])
            else:
                o["words"] = [{"ur": x, "sym": None} for x in (o.get("en") or "").split()]
                o["ur"] = o.get("en") or ""
            o["en"] = ur_sentence
        return
    if LANG == "en" and isinstance(o.get("ur"), str):
        en = o.get("en")
        if isinstance(en, str) and en.strip():
            o["ur"], o["en"] = en, o["ur"]
    for v in o.values():
        if isinstance(v, (dict, list)): localize(v)


def transform(o, n):
    if isinstance(o, list):
        for x in o: transform(x, n)
        return
    if not isinstance(o, dict): return
    if isinstance(o.get("crop"), list):
        o["src"], o["w"], o["h"] = crop_src(n, o.pop("crop"))
    if isinstance(o.get("img"), list):
        o["imgSrc"], _, _ = crop_src(n, o.pop("img"))
    if "sym" in o:
        s = o.pop("sym")
        if isinstance(s, str):
            src = sym_src(s)
            if src: o["symSrc"] = src
    if isinstance(o.get("words"), list) and "ur" not in o:
        o["ur"] = " ".join(w["ur"].strip() for w in o["words"])
    if isinstance(o.get("ur"), str) and o["ur"].strip():
        a = reg_audio(o["ur"])
        if a: o["a"] = a
    for k, v in list(o.items()):
        if isinstance(v, (dict, list)): transform(v, n)


async def tts_all(todo):
    import edge_tts
    sem = asyncio.Semaphore(18)
    done = 0

    async def one(i, ur):
        nonlocal done
        text = speak_text(ur)
        path = f"{OUT}/assets/audio/{i}.mp3"
        for attempt in range(4):
            try:
                async with sem:
                    c = edge_tts.Communicate(text, VOICE, rate=RATE, boundary="WordBoundary")
                    ev = []; buf = bytearray()
                    async for ch in c.stream():
                        if ch["type"] == "audio": buf += ch["data"]
                        elif ch["type"] == "WordBoundary": ev.append(ch)
                if len(buf) < 500: raise RuntimeError("empty audio")
                with open(path, "wb") as f: f.write(buf)
                # map word boundaries onto character offsets of the ORIGINAL string
                m = []; cur = 0
                for e in ev:
                    w = e["text"].strip()
                    if not w: continue
                    p = ur.find(w, cur)
                    if p < 0:
                        p = ur.find(w[: max(1, len(w) // 2)], cur)
                        if p < 0: continue
                    m.append([round(e["offset"] / 10000), p])
                    cur = p + 1
                marks[i] = m
                break
            except Exception as ex:
                if attempt == 3: print("  TTS failed:", i, text[:40], ex)
                await asyncio.sleep(1.5 * (attempt + 1))
        done += 1
        if done % 200 == 0:
            print(f"  audio {done}/{len(todo)}", flush=True)
            json.dump(marks, open(MARKS_F, "w"))

    await asyncio.gather(*(one(i, u) for i, u in todo))


def main():
    files = sorted(glob.glob("content/p*.json"))
    if DO_SYM:
        # prefetch all symbol keywords in parallel
        from concurrent.futures import ThreadPoolExecutor
        kws = set()
        def coll(o):
            if isinstance(o, dict):
                if isinstance(o.get("sym"), str): kws.add(o["sym"].strip().lower())
                for v in o.values(): coll(v)
            elif isinstance(o, list):
                for v in o: coll(v)
        for fn in files:
            try: coll(json.load(open(fn, encoding="utf-8")))
            except Exception: pass
        kws = [k for k in kws if k and (SYM_OVERRIDE.get(k, k) or 'x') not in sym_cache and SYM_OVERRIDE.get(k, k)]
        print("symbols to fetch:", len(kws), flush=True)
        with ThreadPoolExecutor(8) as ex:
            list(ex.map(sym_src, kws))
        json.dump(sym_cache, open(SYM_CACHE_F, "w"), indent=0, sort_keys=True)
    pages = []
    for fn in files:
        try:
            d = json.load(open(fn, encoding="utf-8"))
        except Exception as ex:
            print("SKIP (bad json):", fn, ex); continue
        localize(d)
        transform(d, d["n"])
        pages.append(d)
    json.dump(sym_cache, open(SYM_CACHE_F, "w"), indent=0, sort_keys=True)

    todo = [(i, u) for i, u in need_audio.items() if not os.path.exists(f"{OUT}/assets/audio/{i}.mp3") or i not in marks]
    print(f"pages: {len(pages)}  audio clips: {len(need_audio)}  missing: {len(todo)}")

    ui = json.load(open("tools/ui_strings.json", encoding="utf-8"))
    localize(ui)
    transform(ui, 0)
    todo += [(i, u) for i, u in need_audio.items() if (not os.path.exists(f"{OUT}/assets/audio/{i}.mp3") or i not in marks) and (i, u) not in todo]
    if DO_TTS and todo:
        asyncio.run(tts_all(todo))
        json.dump(marks, open(MARKS_F, "w"))
    index = {"lang": LANG, "total": 96, "pages": [], "chapters": {}, "ui": ui, "uiMarks": {v["a"]: marks[v["a"]] for v in ui.values() if v.get("a") in marks}}
    for d in pages:
        n = d["n"]
        ids = set()

        def collect(o):
            if isinstance(o, dict):
                if isinstance(o.get("a"), str): ids.add(o["a"])
                for v in o.values(): collect(v)
            elif isinstance(o, list):
                for v in o: collect(v)
        collect(d)
        d["marks"] = {i: marks[i] for i in ids if i in marks and os.path.exists(f"{OUT}/assets/audio/{i}.mp3")}
        d["noaudio"] = [i for i in ids if not os.path.exists(f"{OUT}/assets/audio/{i}.mp3")]
        with open(f"{OUT}/{DATA}/p{n:03d}.js", "w", encoding="utf-8") as f:
            f.write(f"window.ADT_PAGE&&window.ADT_PAGE({json.dumps(d, ensure_ascii=False, separators=(',', ':'))});\n")
        has_act = any(b.get("t") == "activity" for b in d.get("blocks", []))
        index["pages"].append({"n": n, "printed": d.get("printed", ""), "chapter": d.get("chapter", 0), "kind": d.get("kind"),
                               "title": {"ur": d["title"]["ur"], "en": d["title"].get("en", "")}, "act": has_act, "easy": bool(d.get("easy"))})
        if d.get("kind") == "opener":
            index["chapters"][str(d["chapter"])] = {"ur": d["title"]["ur"], "en": d["title"].get("en", "")}
    with open(f"{OUT}/{DATA}/index.js", "w", encoding="utf-8") as f:
        f.write(f"window.ADT_INDEX={json.dumps(index, ensure_ascii=False, separators=(',', ':'))};\n")
    print("built", len(pages), "pages")


if __name__ == "__main__":
    main()
