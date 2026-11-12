#!/usr/bin/env python3
"""Comparison for illustrated scenes with small faces (pages 26-28).
   Writes qa/compare2/<id>_<method>.jpg, manifest.json and the page in qa/compare2_page/."""
import base64, io, json, os, shutil, sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import upscale as U
import compare as C

OUT = "qa/compare2"; PAGE = "qa/compare2_page"
os.makedirs(OUT, exist_ok=True); os.makedirs(PAGE + "/img", exist_ok=True)
PICS = [(26, "e8396d1614", "Chand Raat bazaar"), (27, "45d461639f", "Eid al-Adha courtyard"), (28, "395ef6101e", "Holi"),
        (28, "52945088d3", "Baisakhi"), (28, "b55f00041d", "Christmas tree")]
ROWS = {(r["n"], r["k"]): r for r in json.load(open("qa/upscale/classify.json"))}
ANIME = "xinntao/realesrgan@1b976a4d456ed9e4d1a846597b7614e79eadad3032e9124fa63859db0fd59b56"
MODELS = {
    "anime": (ANIME, lambda uri: {"img": uri, "scale": 4, "version": "Anime - anime6B", "face_enhance": False}),
    "esrgan": (ANIME, lambda uri: {"img": uri, "scale": 4, "version": "General - RealESRGANplus", "face_enhance": False}),
    "crystal": C.MODELS["crystal"], "gpt": C.MODELS["gpt"], "banana": C.MODELS["banana"],
}


def one(job):
    pid, m, uri = job
    fn = f"{OUT}/{pid}_{m}.jpg"
    if os.path.exists(fn): return
    slug, mk = MODELS[m]
    data, met = C.run_model(slug, mk(uri))
    if data: Image.open(io.BytesIO(data)).convert("RGB").save(fn, quality=92)
    print(pid, m, "ok" if data else met, flush=True)


def main():
    jobs = []; man = []
    for n, k, label in PICS:
        r = ROWS[(n, k)]; pid = f"p{n:03d}_{k}"; nat = U.native(n, r["c"])
        nat.save(f"{OUT}/{pid}_orig.png")
        Image.open(f"qa/upscale/final/{pid}.png").convert("RGB").save(f"{OUT}/{pid}_recraft.jpg", quality=92)
        buf = io.BytesIO(); nat.save(buf, "PNG"); uri = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
        jobs += [(pid, m, uri) for m in MODELS]
        man.append({"id": pid, "page": n, "label": label, "native": list(nat.size), "v": {}})
    with ThreadPoolExecutor(2) as ex: list(ex.map(one, jobs))
    for e in man:
        for m in ["orig", "recraft"] + list(MODELS):
            f = f"{e['id']}_{m}." + ("png" if m == "orig" else "jpg")
            if os.path.exists(f"{OUT}/{f}"):
                e["v"][m] = {"file": f, "size": list(Image.open(f"{OUT}/{f}").size)}; shutil.copy(f"{OUT}/{f}", f"{PAGE}/img/{f}")
            else: e["v"][m] = {"error": "failed"}
    json.dump(man, open(f"{OUT}/manifest.json", "w"), indent=1)
    t = open("tools/compare_template.html", encoding="utf-8").read().replace("__MANIFEST__", json.dumps(man))
    t = t.replace("<title>Upscaling Comparison</title>", "<title>Cartoon Faces Comparison</title>").replace("<h1>Upscaling comparison</h1>", "<h1>Cartoon faces: upscaling comparison</h1>")
    t = t.replace("recraft: 'Recraft Crisp'", "recraft: 'Recraft Crisp (in the book now)', anime: 'Real-ESRGAN Anime'").replace("orig: 'as in the book now'", "orig: 'the scan', anime: 'keeps pixels · $0.002'")
    t = t.replace("const ORDER = ['orig', 'esrgan', 'topaz', 'topaztext', 'recraft', 'crystal', 'clarity', 'gpt', 'banana'];", "const ORDER = ['orig', 'recraft', 'esrgan', 'anime', 'crystal', 'gpt', 'banana'];")
    open(f"{PAGE}/cartoon-faces-comparison.html", "w", encoding="utf-8").write(t)
    print("page written")


if __name__ == "__main__":
    main()
