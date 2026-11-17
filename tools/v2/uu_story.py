#!/usr/bin/env python3
"""Vertical STORY Shorts (1080x1920): one big fact told as a documentary, NOT a ranking.

Use this for "how / why / what happened" topics. Use uu_render.py's rank/roll scenes only for real comparisons.
usage: uu_story.py spec.json still t1,t2 | full        (spec "format": "story"; header = the one big fact, shown all along)

Scene types:
  photo   {img*, kicker, big, lines[]}                 full-bleed Ken Burns photo, caption block low-centre, auto credit
  counter {from*, to*, y0, y1, label, chip}           big number ticking down/up with the years, shrinking bar
  bulb    {kicker, big, lines[]}                      a bomb outline morphing into a glowing light bulb
  outro   (uu_render's vertical outro: lines + subscribe card; "card": "youtube" for short edits)
Images are repo-relative ($UU_REPO); spec["credits_from"] may be one path or a list of credits.json files.
"""
import json, math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import uu_render as R
from uu_render import (W, H, T, F, WHITE, MUTED, clamp, ease, ease_io, back, prog, text_a, rect_a, paste_a, typed,
                       fit_font, chrome, big_number, GLOBE)

REPO = os.environ.get("UU_REPO", "/home/claude/unknown-uncovered")
CREDITS = {}
cf = R.SPEC.get("credits_from") or []
for p in ([cf] if isinstance(cf, str) else cf):
    if os.path.exists(os.path.join(REPO, p)):
        d = json.load(open(os.path.join(REPO, p)))
        CREDITS.update({os.path.join(os.path.dirname(p), k): v for k, v in d.items()})

_img = {}
def load(path):
    if path in _img: return _img[path]
    full = os.path.join(REPO, path)
    im = Image.open(full).convert("RGB") if os.path.exists(full) else Image.new("RGB", (W, H), (20, 24, 20))
    s = max(W * 1.2 / im.width, H * 1.2 / im.height)
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    _img[path] = im; return im

def kenburns(img, path, t, D, k):
    src = load(path); p = ease_io(t / max(D, 0.1))
    z = 1.0 + 0.14 * (p if k % 2 == 0 else 1 - p)
    cw, ch = W * 1.16 / z, H * 1.16 / z
    dx = (src.width - cw) * (0.5 + 0.3 * math.sin(k * 1.9) * (p - 0.5))
    dy = (src.height - ch) * (0.5 + 0.2 * math.cos(k * 1.1) * (p - 0.5))
    fr = src.crop((int(dx), int(dy), int(dx + cw), int(dy + ch))).resize((W, H), Image.BILINEAR).convert("RGBA")
    img.paste(fr, (0, 0))

_shade = None
def shade(img):
    global _shade
    if _shade is None:
        y = np.linspace(0, 1, H)
        a = np.clip((y - 0.42) / 0.5, 0, 1) ** 1.1 * 0.92 + np.clip((0.16 - y) / 0.16, 0, 1) * 0.55
        lay = np.zeros((H, W, 4), np.uint8); lay[..., 3] = (np.tile(a[:, None], (1, W)) * 255).astype(np.uint8)
        _shade = Image.fromarray(lay, "RGBA")
    img.alpha_composite(_shade)

def credit(img, path, a=1.0):
    c = CREDITS.get(path)
    if not c: return
    who = (c.get("artist") or c.get("credit") or "Wikimedia Commons")[:48]
    text_a(img, (W / 2, 1640), f"Image: {who} · {c.get('license', '')} · Wikimedia Commons", F("inter", 19, "Medium"),
           (210, 210, 205), 0.8 * a, "mm", shadow=3)

def caption(img, sc, t, D, y0=1110):
    text_a(img, (W / 2, y0), typed(sc.get("kicker", ""), prog(t, 0.2, 0.6)), F("mono", 32), T["accent"], 1, "mm", shadow=4)
    if sc.get("big"):
        g = back(clamp((t - 0.5) / 0.5)); s = sc["big"]
        f = fit_font("anton", int(230 * (0.85 + 0.15 * clamp(g, 0, 1.2))), s, W - 120)
        text_a(img, (W / 2, y0 + 170), s, f, WHITE, clamp((t - 0.5) / 0.25), "mm", shadow=12)
    for i, ln in enumerate(sc.get("lines", [])):
        st = 1.0 + i * 0.7
        text_a(img, (W / 2, y0 + 330 + i * 70), typed(ln, prog(t, st, 0.7)), fit_font("disp", 54, ln, W - 120, "Bold"),
               (238, 236, 228), 1, "mm", shadow=8)

def sc_photo(img, sc, t, D, tg, k):
    kenburns(img, sc["img"], t, D, k)
    img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * sc.get("dark", 0.22)))))
    shade(img)
    caption(img, sc, t, D)
    credit(img, sc["img"], clamp(t / 0.6))
    chrome(img, tg)

def sc_counter(img, sc, t, D, tg, k):
    g = GLOBE.render(30, 40 + tg * 4, dim_others=0.3)
    paste_a(img, g, (W / 2 - g.width / 2, 520 - g.height / 2), 0.4)
    p = prog(t, 0.8, max(2.0, D * 0.6))
    y0s, y1s = str(sc.get("y0", "")), str(sc.get("y1", ""))   # no fake in-between years: only the real data points
    y = y0s if p <= 0.0 else (y1s if p > 0.98 else f"{y0s} → {y1s}")
    v = sc["to"] if p > 0.98 else int(round(sc["from"] + (sc["to"] - sc["from"]) * p))
    a = clamp(t / 0.4)
    text_a(img, (W / 2, 820), y, F("anton", 120) if "→" not in y else F("disp", 90, "Black"), T["accent"], a, "mm", shadow=8)
    text_a(img, (W / 2, 1010), f"{v:,}", F("anton", 250), WHITE, a, "mm", shadow=14)
    text_a(img, (W / 2, 1180), sc.get("label", ""), fit_font("disp", 50, sc.get("label", ""), W - 140, "Black"), MUTED, a, "mm")
    bw = (W - 200) * (v / max(sc["from"], sc["to"]))
    rect_a(img, (100, 1260, W - 100, 1300), (40, 40, 40), 0.9 * a, 20)
    rect_a(img, (100, 1260, 100 + bw, 1300), T["alert"] if p > 0.5 else T["accent"], a, 20)
    if sc.get("chip") and p > 0.98:
        ca = clamp((t - 0.8 - max(2.0, D * 0.6)) / 0.3)
        f = F("anton", 90); s = sc["chip"]; w = ImageDraw.Draw(img).textlength(s, font=f)
        rect_a(img, (W / 2 - w / 2 - 36, 1350, W / 2 + w / 2 + 36, 1480), T["alert"], ca, 24)
        text_a(img, (W / 2, 1415), s, f, WHITE, ca, "mm")
    chrome(img, tg, a)

def _bomb(d, cx, cy, s, col):
    d.rounded_rectangle([cx - 90 * s, cy - 220 * s, cx + 90 * s, cy + 160 * s], radius=int(90 * s), outline=col, width=int(12 * s))
    for sx in (-1, 1):
        d.polygon([(cx + sx * 60 * s, cy + 140 * s), (cx + sx * 150 * s, cy + 280 * s), (cx + sx * 40 * s, cy + 250 * s)], outline=col, width=int(10 * s))
    d.line([cx, cy + 160 * s, cx, cy + 270 * s], fill=col, width=int(10 * s))

def _bulb(d, cx, cy, s, col):
    d.ellipse([cx - 150 * s, cy - 260 * s, cx + 150 * s, cy + 40 * s], outline=col, width=int(12 * s))
    d.line([cx - 70 * s, cy + 30 * s, cx - 70 * s, cy + 130 * s], fill=col, width=int(12 * s))
    d.line([cx + 70 * s, cy + 30 * s, cx + 70 * s, cy + 130 * s], fill=col, width=int(12 * s))
    for i in range(3):
        yy = cy + (140 + i * 34) * s
        d.line([cx - 75 * s, yy, cx + 75 * s, yy], fill=col, width=int(12 * s))
    d.line([cx - 40 * s, cy - 40 * s, cx - 15 * s, cy - 120 * s, cx + 15 * s, cy - 40 * s, cx + 40 * s, cy - 120 * s], fill=col, width=int(8 * s))

def sc_bulb(img, sc, t, D, tg, k):
    cx, cy = W / 2, 640
    m = ease_io(clamp((t - 1.0) / 1.6))
    if m > 0.3:
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse([cx - 330, cy - 470, cx + 330, cy + 190], fill=(255, 214, 90, int(170 * (m - 0.3) / 0.7)))
        img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(70)))
    lay_a = Image.new("RGBA", (W, H), (0, 0, 0, 0)); _bomb(ImageDraw.Draw(lay_a), cx, cy - 40, 1.25, T["alert"] + (255,))
    lay_b = Image.new("RGBA", (W, H), (0, 0, 0, 0)); _bulb(ImageDraw.Draw(lay_b), cx, cy + 40, 1.25, (255, 222, 120, 255))
    paste_a(img, lay_a, (0, 0), (1 - m) * clamp(t / 0.4)); paste_a(img, lay_b, (0, 0), m)
    if 0.05 < m < 0.95:
        r = np.random.default_rng(int(tg * 100))
        dd = ImageDraw.Draw(img)
        for _ in range(40):
            a = r.uniform(0, 6.28); rr = r.uniform(100, 380) * m
            dd.ellipse([cx + rr * math.cos(a) - 4, cy + rr * math.sin(a) - 4, cx + rr * math.cos(a) + 4, cy + rr * math.sin(a) + 4], fill=(255, 230, 150, 220))
    caption(img, sc, t, D, 1130)
    chrome(img, tg)

def sc_iceberg(img, sc, t, D, tg, k):
    """Iceberg: the announced number is the tip above water; the silent part below is big and uncounted."""
    wl = 760                                                         # water line
    a = clamp(t / 0.4); d = ImageDraw.Draw(img)
    text_a(img, (W / 2, 250), typed(sc.get("kicker", ""), prog(t, 0.1, 0.6)), F("mono", 34), T["accent"], 1, "mm", shadow=4)
    # water
    sea = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sea).rectangle([0, wl, W, 1620], fill=(14, 40, 78, int(150 * a)))
    img.alpha_composite(sea)
    for x in range(0, W, 6):
        y = wl + 6 * math.sin(x / 60 + tg * 2.4)
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=T["accent"] + (int(200 * a),))
    # tip
    pt = prog(t, 0.3, 0.8); dy = (1 - pt) * 160
    tip = [(W / 2 - 170, wl), (W / 2 - 60, wl - 230 + dy), (W / 2 + 10, wl - 180 + dy), (W / 2 + 90, wl - 300 + dy), (W / 2 + 190, wl)]
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(lay).polygon(tip, fill=(232, 240, 250, 255))
    paste_a(img, lay, (0, 0), pt)
    text_a(img, (W / 2, wl - 420), sc.get("top_label", "ANNOUNCED"), F("disp", 46, "Black"), WHITE, pt, "mm", shadow=8)
    text_a(img, (W / 2, wl - 350), sc.get("top_value", ""), F("anton", 64), T["accent"], pt, "mm", shadow=8)
    # the hidden mass
    pb = prog(t, sc.get("reveal_at", 2.2), 1.2)
    if pb > 0:
        body = [(W / 2 - 170, wl), (W / 2 - 420, wl + 300), (W / 2 - 380, wl + 640), (W / 2 - 80, wl + 820), (W / 2 + 300, wl + 700),
                (W / 2 + 440, wl + 360), (W / 2 + 190, wl)]
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(lay).polygon(body, fill=(120, 170, 220, 120), outline=(190, 220, 255, 220))
        paste_a(img, lay, (0, (1 - pb) * -120), pb)
        text_a(img, (W / 2, wl + 330), "?", F("anton", 300), T["alert"], pb, "mm", shadow=12)
        text_a(img, (W / 2, wl + 560), sc.get("bottom_label", "SILENT LAYOFFS"), F("disp", 58, "Black"), WHITE, pb, "mm", shadow=8)
        text_a(img, (W / 2, wl + 630), sc.get("bottom_sub", "never announced · never counted"), F("inter", 36, "SemiBold"), T["accent2"], pb, "mm", shadow=6)
    for i in range(14):                                              # rising bubbles
        bx = (i * 173 + 90) % W; by = 1600 - ((tg * 90 + i * 113) % 840)
        d.ellipse([bx - 5, by - 5, bx + 5, by + 5], outline=T["accent"] + (120,), width=2)
    chrome(img, tg, a)

R.SCENE_FN.update({"iceberg": sc_iceberg})
R.SCENE_FN.update({"photo": sc_photo, "counter": sc_counter, "bulb": sc_bulb})

if __name__ == "__main__":
    R.main()
