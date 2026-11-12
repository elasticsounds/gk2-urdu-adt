#!/usr/bin/env python3
"""Upscaling comparison: original vs Real-ESRGAN vs GPT image vs Nano Banana, for a few pictures.
   Writes qa/compare/<id>_<method>.jpg and qa/compare/manifest.json"""
import base64, io, json, os, sys, time, urllib.request
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import upscale as U

OUT = "qa/compare"
os.makedirs(OUT, exist_ok=True)
PICS = [
    (9, [0.173, 0.123, 0.467, 0.282], "Badshahi Mosque, Lahore (small photo)"),
    (9, [0.13, 0.51, 0.848, 0.8], "Kabaddi match (wide photo)"),
    (6, [0.17, 0.36, 0.81, 0.905], "Map of Pakistan (with Urdu labels)"),
    (12, [0.145, 0.198, 0.517, 0.428], "Children in an apple orchard (small photo)"),
    (27, [0.105, 0.175, 0.452, 0.345], "Eid: people in a courtyard (small photo)"),
    (27, [0.12, 0.598, 0.86, 0.88], "Mosque at night (wide photo)"),
]
PROMPT = ("Upscale and restore this low-resolution scanned picture from a printed school textbook to a sharp, high-resolution image. "
          "Keep the composition, framing, colours, people, faces, clothing, objects and every piece of text and lettering exactly the same. "
          "Do not add, remove, move, crop or restyle anything. Only remove blur, JPEG artefacts and print halftone noise, and restore natural fine detail.")
MODELS = {
    "gpt": ("openai/gpt-image-2.5-flare", lambda uri: {"prompt": PROMPT, "input_images": [uri], "aspect_ratio": "auto", "quality": "high", "output_format": "png"}),
    "banana": ("google/nano-banana-2", lambda uri: {"prompt": PROMPT, "image_input": [uri], "aspect_ratio": "match_input_image", "resolution": "2K", "output_format": "png"}),
    "topaz": ("topazlabs/image-upscale", lambda uri: {"image": uri, "enhance_model": "Low Resolution V2", "upscale_factor": "4x", "output_format": "png"}),
    "topaztext": ("topazlabs/image-upscale", lambda uri: {"image": uri, "enhance_model": "Text Refine", "upscale_factor": "4x", "output_format": "png"}),
    "recraft": ("recraft-ai/recraft-crisp-upscale", lambda uri: {"image": uri}),
    "crystal": ("philz1337x/crystal-upscaler", lambda uri: {"image": uri, "scale_factor": 4, "creativity": 0, "output_format": "png"}),
    "clarity": ("philz1337x/clarity-upscaler@dfad41707589d68ecdccd1dfa600d55a208f9310748e44bfe35b4a6291453d5e", lambda uri: {"image": uri, "scale_factor": 4, "creativity": 0.25, "resemblance": 1.0, "output_format": "png"}),
    "supir": ("cjwbw/supir@1302b550b4f7681da87ed0e405016d443fe1fafd64dabce6673401855a5039b5", lambda uri: {"image": uri, "upscale": 4, "model_name": "SUPIR-v0Q"}),
}


def run_model(slug, inp):
    for attempt in range(6):
        try:
            if "@" in slug: p = U.api("https://api.replicate.com/v1/predictions", {"version": slug.split("@")[1], "input": inp})
            else: p = U.api(f"https://api.replicate.com/v1/models/{slug}/predictions", {"input": inp})
            t0 = time.time()
            while p["status"] not in ("succeeded", "failed", "canceled") and time.time() - t0 < 900:
                time.sleep(3); p = U.api(p["urls"]["get"])
            if p["status"] != "succeeded": raise RuntimeError(str(p.get("error") or p["status"])[:300])
            out = p["output"][0] if isinstance(p["output"], list) else p["output"]
            with urllib.request.urlopen(urllib.request.Request(out, headers={"User-Agent": "curl/8.7.1"}), timeout=180) as r:
                return r.read(), p.get("metrics", {})
        except Exception as ex:
            print("   retry", slug, str(ex)[:200], flush=True)
            if attempt == 5 or ("429" not in str(ex) and attempt >= 1): return None, {"error": str(ex)[:300]}
            time.sleep(15)


def main():
    man = []
    for n, c, label in PICS:
        pid = f"p{n:03d}_{U.key(n, c)}"
        nat = U.native(n, c)
        entry = {"id": pid, "page": n, "label": label, "native": list(nat.size), "v": {}}
        nat.save(f"{OUT}/{pid}_orig.png")
        entry["v"]["orig"] = {"file": f"{pid}_orig.png", "size": list(nat.size)}
        e = U.upscale(n, k=U.key(n, c), c=c)
        if e:
            im = Image.open(e).convert("RGB"); im.save(f"{OUT}/{pid}_esrgan.jpg", quality=92)
            entry["v"]["esrgan"] = {"file": f"{pid}_esrgan.jpg", "size": list(im.size)}
        buf = io.BytesIO(); nat.save(buf, "PNG")
        uri = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
        for m, (slug, mk) in MODELS.items():
            fn = f"{OUT}/{pid}_{m}.jpg"
            if not os.path.exists(fn):
                print(pid, m, "...", flush=True)
                data, met = run_model(slug, mk(uri))
                if not data:
                    entry["v"][m] = {"error": met.get("error", "failed")}; continue
                entry.setdefault("secs", {})[m] = met.get("predict_time")
                Image.open(io.BytesIO(data)).convert("RGB").save(fn, quality=92)
            im = Image.open(fn)
            entry["v"][m] = {"file": f"{pid}_{m}.jpg", "size": list(im.size)}
        man.append(entry)
        json.dump(man, open(f"{OUT}/manifest.json", "w"), indent=1)
        print(pid, {k: v.get("size") or v.get("error") for k, v in entry["v"].items()}, flush=True)


if __name__ == "__main__":
    main()
