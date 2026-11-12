#!/usr/bin/env python3
"""Remove a repeated, semi-transparent grey watermark from every page of a PDF.

    python dewatermark.py book.pdf out_dir [--dpi N] [--region x0,y0,x1,y1] [--min-pages 8]

How it works
  1. Render every page to an image, at the resolution of the scan inside the PDF
     (resampling a scan smears the watermark edges and leaves traces behind).
  2. Learn the watermark: on each page, find the parts that would be blank paper if the
     watermark were not there. At every pixel, take the median darkness over all pages
     where that pixel is blank. Page content differs from page to page and drops out;
     the watermark is the same everywhere and is what remains.
  3. Turn that into an opacity map (0 = no watermark, 0.6 = strongest allowed).
  4. For each page, measure how strongly the watermark is present (it can be fainter on
     some pages, or missing), then undo the blend:  original = seen / (1 - opacity) ** strength
  5. Save cleaned page images, a cleaned PDF, and a picture of the learned watermark.

It needs the watermark to be in the same place on most pages, grey or black, and laid over
the page (not hidden behind it). It needs a fair number of pages with blank paper under each
part of the watermark. --region limits the work to a box, given as fractions of the page
(e.g. 0.15,0.2,0.5,0.45); without it the largest repeated faint mark is found automatically.

Requires: pip install pymupdf numpy opencv-python pillow
"""
import argparse, os, sys, warnings
import numpy as np, cv2, pymupdf
from PIL import Image


def native_dpi(doc):
    """Resolution of the page scans inside the PDF (the largest embedded image on the first pages)."""
    best = []
    for page in list(doc)[:12]:
        ims = [(i[2] * i[3], i[2]) for i in page.get_images(full=True)]
        if ims: best.append(max(ims)[1] / (page.rect.width / 72))  # the image with the most pixels is the page scan
    return int(round(float(np.median(best)))) if best else 150


def render(pdf, dpi):
    doc = pymupdf.open(pdf); pages = []
    if not dpi:
        dpi = min(300, max(72, native_dpi(doc))); print("rendering at", dpi, "dpi (the scan's own resolution)")
    for page in doc:
        pix = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csRGB, alpha=False)
        pages.append(np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3).copy())
    sizes = {p.shape for p in pages}
    if len(sizes) > 1:  # mixed page sizes: bring everything to the most common size
        common = max(sizes, key=lambda s: sum(p.shape == s for p in pages))
        pages = [p if p.shape == common else cv2.resize(p, (common[1], common[0]), interpolation=cv2.INTER_AREA) for p in pages]
    return pages, [(p.rect.width, p.rect.height) for p in doc]


def blank_paper(rgb):
    """True where the page would be blank paper apart from a faint overlay."""
    f = rgb.astype(np.float32); g = f.mean(-1); sat = f.max(-1) - f.min(-1)
    mostly_white = cv2.blur((g >= 246).astype(np.float32), (41, 41)) > 0.55
    no_ink = cv2.blur((g < 150).astype(np.float32), (25, 25)) < 0.004
    no_colour = cv2.dilate(sat, np.ones((9, 9), np.uint8)) < 16
    return mostly_white & no_ink & no_colour, g


def learn(pages, min_pages, strip=64):
    N = len(pages); H, W, _ = pages[0].shape
    dark = np.empty((N, H, W), np.float32)
    for i, p in enumerate(pages):
        ok, g = blank_paper(p)
        d = 255.0 - g; d[~ok] = np.nan; dark[i] = d
    T = np.zeros((H, W), np.float32)
    for y in range(0, H, strip):  # in strips, to keep memory down
        s = dark[:, y:y + strip]
        cnt = np.isfinite(s).sum(0)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            m = np.nanmedian(s, axis=0)
        m[(cnt < min_pages) | ~np.isfinite(m)] = 0
        T[y:y + strip] = m
    T[T < 2.5] = 0  # below scanner noise
    return T


def main_region(T):
    """Bounding box of the largest connected faint mark."""
    blob = cv2.dilate((T > 6).astype(np.uint8), np.ones((31, 31), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(blob)
    if n < 2: return None
    k = 1 + int(np.argmax([T[lab == j].sum() for j in range(1, n)]))
    x, y, w, h = stats[k, :4]
    return x, y, x + w, y + h


def highpass(g):
    return g - cv2.GaussianBlur(g, (0, 0), 4)


def clean(page, T, box):
    """Returns (cleaned page, strength). Strength near 1 = watermark fully present; near 0 = absent."""
    x0, y0, x1, y1 = box
    t = T[y0:y1, x0:x1]; a = np.clip(t / 255.0, 0, 0.6)
    mask = cv2.dilate((t > 0).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    R = page[y0:y1, x0:x1].astype(np.float32)
    Lh = highpass(-np.log(np.clip(R.mean(-1), 8, 255) / 255.0))  # page, as optical density, fine detail only
    Ah = highpass(-np.log(1 - a))                                  # watermark, same treatment
    sel = mask.copy(); s = 0.0
    for _ in range(4):  # fit strength, ignoring the 30% of pixels that fit worst (text, pictures)
        s = float((Lh * Ah)[sel].sum() / ((Ah * Ah)[sel].sum() + 1e-6))
        res = np.abs(Lh - s * Ah); sel = mask & (res <= np.percentile(res[mask], 70))
    if s <= 0.3: return page, s
    fixed = np.clip(R / ((1 - a[..., None]) ** min(s, 1.15)), 0, 255)
    smooth = cv2.bilateralFilter(fixed.astype(np.uint8), 5, 18, 3).astype(np.float32)  # calm JPEG ringing along the old edges
    m = cv2.GaussianBlur(mask.astype(np.float32), (0, 0), 1.0)[..., None]
    out = page.copy(); out[y0:y1, x0:x1] = (fixed * (1 - m) + smooth * m).astype(np.uint8)
    return out, s


def main():
    ap = argparse.ArgumentParser(description="Remove a repeated semi-transparent watermark from a PDF.")
    ap.add_argument("pdf"); ap.add_argument("out")
    ap.add_argument("--dpi", type=int, default=0, help="default: the resolution of the scan inside the PDF")
    ap.add_argument("--region", help="x0,y0,x1,y1 as fractions of the page")
    ap.add_argument("--min-pages", type=int, default=8, help="pages that must show blank paper at a pixel before it is trusted")
    ap.add_argument("--quality", type=int, default=90)
    a = ap.parse_args()
    os.makedirs(a.out + "/pages", exist_ok=True)
    pages, rects = render(a.pdf, a.dpi)
    H, W, _ = pages[0].shape
    print(f"{len(pages)} pages at {W}x{H}")
    T = learn(pages, min(a.min_pages, max(2, len(pages) // 3)))
    if a.region:
        fx0, fy0, fx1, fy1 = map(float, a.region.split(","))
        box = (int(fx0 * W), int(fy0 * H), int(fx1 * W), int(fy1 * H))
    else:
        box = main_region(T)
    if not box or T[box[1]:box[3], box[0]:box[2]].max() < 6:
        sys.exit("No repeated faint watermark found. Try --region, or a lower --min-pages.")
    keep = np.zeros_like(T); keep[box[1]:box[3], box[0]:box[2]] = T[box[1]:box[3], box[0]:box[2]]; T = keep
    Image.fromarray(np.clip(255 - T * 3, 0, 255).astype(np.uint8)).save(a.out + "/watermark_learned.png")
    print("watermark box (fractions):", ",".join(f"{v:.3f}" for v in (box[0] / W, box[1] / H, box[2] / W, box[3] / H)),
          "| peak opacity %.2f" % (T.max() / 255))
    doc = pymupdf.open(); skipped = []
    for i, p in enumerate(pages):
        out, s = clean(p, T, box)
        if s <= 0.3: skipped.append((i + 1, round(s, 2)))
        fn = f"{a.out}/pages/p{i + 1:03d}.jpg"
        Image.fromarray(out).save(fn, quality=a.quality)
        w, h = rects[i]; pg = doc.new_page(width=w, height=h); pg.insert_image(pg.rect, filename=fn)
    doc.save(a.out + "/cleaned.pdf", deflate=True)
    print("cleaned", len(pages) - len(skipped), "pages; left untouched (no watermark detected):", skipped or "none")


if __name__ == "__main__":
    main()
