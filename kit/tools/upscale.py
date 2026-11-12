#!/usr/bin/env python3
"""Upscale the cropped pictures with Real-ESRGAN on Replicate.
   python tools/upscale.py --trial            -> six sample pictures into qa/upscale/ + comparison sheet
   python tools/upscale.py --all              -> every crop used by the book, cached in qa/upscale/x4/
Needs REPLICATE_API_TOKEN in the environment. Nothing but the cropped picture is sent."""
import base64, glob, hashlib, io, json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
TOKEN = os.environ.get("REPLICATE_API_TOKEN", "")
VERSION = "b3ef194191d13140337468c916c2c5b96dd0cb06dffc032a022a31807f6a5ea8"  # nightmareai/real-esrgan
OUT = "qa/upscale/x4"
os.makedirs(OUT, exist_ok=True)
pages = {}


def page(n):
    if n not in pages:
        pages[n] = Image.open(f"adt/assets/pages/p{n:03d}.jpg").convert("RGB")
    return pages[n]


def key(n, c):
    return hashlib.sha1(json.dumps([n, [round(x, 4) for x in c]]).encode()).hexdigest()[:10]


def native(n, c):
    im = page(n); W, H = im.size
    return im.crop((round(c[0] * W), round(c[1] * H), round(c[2] * W), round(c[3] * H)))


def crops():
    seen = {}
    def walk(o, n):
        if isinstance(o, dict):
            for k in ("crop", "img"):
                if isinstance(o.get(k), list) and len(o[k]) == 4 and all(isinstance(x, (int, float)) for x in o[k]):
                    seen[(n, key(n, o[k]))] = o[k]
            for v in o.values(): walk(v, n)
        elif isinstance(o, list):
            for v in o: walk(v, n)
    for fn in sorted(glob.glob("content/p*.json")):
        d = json.load(open(fn, encoding="utf-8")); walk(d, d["n"])
    return [(n, k, c) for (n, k), c in seen.items()]


def api(url, body=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body else None,
                                 headers={"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json", "Prefer": "wait=60", "User-Agent": "curl/8.7.1"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())


def upscale(n, k, c):
    path = f"{OUT}/p{n:03d}_{k}.png"
    if os.path.exists(path): return path
    buf = io.BytesIO(); native(n, c).save(buf, "PNG")
    uri = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    for attempt in range(6):
        try:
            p = api("https://api.replicate.com/v1/predictions", {"version": VERSION, "input": {"image": uri, "scale": 4, "face_enhance": False}})
            t0 = time.time()
            while p["status"] not in ("succeeded", "failed", "canceled") and time.time() - t0 < 180:
                time.sleep(2); p = api(p["urls"]["get"])
            if p["status"] != "succeeded": raise RuntimeError(p.get("error") or p["status"])
            out = p["output"][0] if isinstance(p["output"], list) else p["output"]
            with urllib.request.urlopen(urllib.request.Request(out, headers={"User-Agent": "curl/8.7.1"}), timeout=120) as r, open(path, "wb") as f: f.write(r.read())
            return path
        except Exception as ex:
            if attempt == 5: print("  FAILED", n, k, ex, flush=True); return None
            time.sleep(15 if "429" in str(ex) else 4 * (attempt + 1))


def run_official(slug, inp, path):
    """Run an official Replicate model and save its output image to path (cached)."""
    if os.path.exists(path): return path
    for attempt in range(8):
        try:
            p = api(f"https://api.replicate.com/v1/models/{slug}/predictions", {"input": inp})
            t0 = time.time()
            while p["status"] not in ("succeeded", "failed", "canceled") and time.time() - t0 < 400:
                time.sleep(2); p = api(p["urls"]["get"])
            if p["status"] != "succeeded": raise RuntimeError(str(p.get("error") or p["status"])[:200])
            out = p["output"][0] if isinstance(p["output"], list) else p["output"]
            with urllib.request.urlopen(urllib.request.Request(out, headers={"User-Agent": "curl/8.7.1"}), timeout=180) as r: data = r.read()
            with open(path, "wb") as f: f.write(data)
            return path
        except Exception as ex:
            if attempt == 7: print("  FAILED", slug, path, str(ex)[:160], flush=True); return None
            time.sleep(12 if "429" in str(ex) else 5)


def apply_all():
    """Crystal for photos, Recraft Crisp for drawings/maps; results cached in qa/upscale/final/."""
    rows = json.load(open("qa/upscale/classify.json"))
    os.makedirs("qa/upscale/final", exist_ok=True)
    ok = 0
    def one(r):
        buf = io.BytesIO(); native(r["n"], r["c"]).save(buf, "PNG")
        uri = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
        path = f"qa/upscale/final/p{r['n']:03d}_{r['k']}.png"
        if r["kind"] in ("photo", "people"):
            return run_official("philz1337x/crystal-upscaler", {"image": uri, "scale_factor": 4, "creativity": 0, "output_format": "png"}, path)
        return run_official("recraft-ai/recraft-crisp-upscale", {"image": uri}, path)
    with ThreadPoolExecutor(int(os.environ.get("UPSCALE_WORKERS", "2"))) as ex:
        for i, res in enumerate(ex.map(one, rows)):
            ok += bool(res)
            if (i + 1) % 20 == 0: print(f"  {i + 1}/{len(rows)} ok {ok}", flush=True)
    print("done", ok, "of", len(rows))


def main():
    if not TOKEN: sys.exit("REPLICATE_API_TOKEN is not set")
    if "--apply" in sys.argv: return apply_all()
    allc = crops()
    if "--trial" in sys.argv:
        want = [6, 7, 8, 16, 33, 54]
        todo = []
        for n in want:
            cs = sorted([x for x in allc if x[0] == n], key=lambda x: -(x[2][2] - x[2][0]) * (x[2][3] - x[2][1]))
            if cs: todo.append(cs[0])
    else:
        todo = allc
    print("pictures:", len(todo), flush=True)
    with ThreadPoolExecutor(int(os.environ.get("UPSCALE_WORKERS", "1"))) as ex:
        res = list(ex.map(lambda t: upscale(*t), todo))
    print("done:", sum(1 for r in res if r), "failed:", sum(1 for r in res if not r))
    if "--trial" in sys.argv:
        rows = []
        for (n, k, c), r in zip(todo, res):
            if not r: continue
            a = native(n, c); b = Image.open(r).convert("RGB")
            # show a detail region at the same on-screen size: left = current (smooth 4x), right = Real-ESRGAN
            w, h = a.size; cw, ch = min(w, 190), min(h, 150); x0, y0 = (w - cw) // 2, (h - ch) // 2
            la = a.crop((x0, y0, x0 + cw, y0 + ch)).resize((cw * 4, ch * 4), Image.LANCZOS)
            lb = b.crop((x0 * 4, y0 * 4, (x0 + cw) * 4, (y0 + ch) * 4))
            row = Image.new("RGB", (cw * 8 + 30, ch * 4 + 34), "white")
            row.paste(la, (10, 28)); row.paste(lb, (cw * 4 + 20, 28))
            d = ImageDraw.Draw(row); d.text((10, 8), f"page {n}: now", fill="black"); d.text((cw * 4 + 20, 8), "Real-ESRGAN x4", fill="black")
            rows.append(row)
        W = max(r.width for r in rows); sheet = Image.new("RGB", (W, sum(r.height for r in rows)), "white"); y = 0
        for r in rows: sheet.paste(r, (0, y)); y += r.height
        sheet.save("qa/upscale/trial_compare.jpg", quality=90); print("sheet", sheet.size)


if __name__ == "__main__":
    main()
