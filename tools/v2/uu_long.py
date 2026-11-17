#!/usr/bin/env python3
"""16:9 long-form scenes for Unknown Uncovered (1920x1080, 30 fps). Same spec/timeline/voice/music pipeline as uu_render.py.

usage: uu_long.py spec.json still t1,t2 | full        (spec has "format": "long")

Scene types (all fields optional unless noted):
  clock      {title, sub, seconds=85, from_minutes=3}                 Doomsday-style clock, hand sweeps to N seconds
  image      {img*, kicker, lines[], code}                             Ken Burns photo, gradient, typed text, auto credit
  disclaimer {lines[]}                                                 calm legal/education card
  chapter    {n, title, img}                                           chapter card over a darkened, blurred photo
  timeline   {title, points[[year, value, label]]}                     line chart drawn over time
  stat       {kicker, value, value_label, label, items[[big, small]]}  big counter + 3 cards
  club       {title, sub, rows[[code, name, year]]}                    3x3 grid of flags revealed one by one
  country    {code*, name, y0, y1, from, to, from_label, chip, facts[]} globe + flag + counter panel
  silos      {title, fields[[name, lat, lon, label]], total}           zoomed globe with pulsing site markers
  compare    {title, sub, years[2], rows[[code, name, v0, v1]]}        before/after bars
  events     {title, events[[year, name, sub]]}                        horizontal treaty/event timeline
  bars       {title, sub, rows[[code, name, value]]}                   ranked horizontal bars (up to 9)
  booklet    {cover, cover_sub, stamp, stamp_at, open_at, pages, pages_at, dims_at, kicker, big, lines}  passport booklet right, text left
  borders    {lock_at, follow_at, lines}                               Europe 1913 open routes -> 1914 locked (lock_at > scene = stays open)
  dossier    {file, ref, rows[[k, v]], stamp, img, kicker, big, lines} file card right, text left
  outro      {lines[]}                                                 closing lines + subscribe card
Images are paths relative to $UU_REPO (default /home/claude/unknown-uncovered); credits come from spec["credits_from"].
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import uu_render as R
from uu_render import (W, H, T, F, WHITE, MUTED, clamp, ease, ease_io, back, prog, text_a, rect_a, paste_a, typed, flag,
                       silhouette, fit_font, chrome, big_number, CENTROID, GLOBE)

REPO = os.environ.get("UU_REPO", "/home/claude/unknown-uncovered")
CREDITS = {}
_cf = R.SPEC.get("credits_from") or []
for _f in ([_cf] if isinstance(_cf, str) else _cf):                  # one credits.json or a list of them
    if os.path.exists(os.path.join(REPO, _f)):
        _c = json.load(open(os.path.join(REPO, _f)))
        CREDITS.update(_c if isinstance(_c, dict) else {os.path.basename(x.get("file", "")): x for x in _c})

# ---------------------------------------------------------------- images
_img = {}
def load(path, blur=0):
    key = (path, blur)
    if key in _img: return _img[key]
    full = os.path.join(REPO, path)
    if not os.path.exists(full):
        im = Image.new("RGB", (W, H), tuple(int(c * 0.6) for c in T["bg"]))
    else:
        im = Image.open(full).convert("RGB")
    s = max(W * 1.18 / im.width, H * 1.18 / im.height)          # cover with 18% headroom for the Ken Burns move
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
    _img[key] = im; return im

def kenburns(img, path, t, D, k, dark=0.35, blur=0):
    src = load(path, blur)
    p = ease_io(t / max(D, 0.1))
    z = 1.0 + 0.12 * (p if k % 2 == 0 else 1 - p)                # alternate zoom in / out per scene
    cw, ch = min(src.width, W * 1.15 / z), min(src.height, H * 1.15 / z)
    dx = (src.width - cw) * (0.5 + 0.35 * math.sin(k * 1.7) * (p - 0.5))
    dy = (src.height - ch) * (0.5 + 0.25 * math.cos(k * 1.3) * (p - 0.5))
    fr = src.crop((int(dx), int(dy), int(dx + cw), int(dy + ch))).resize((W, H), Image.BILINEAR).convert("RGBA")
    img.paste(fr, (0, 0))
    if dark: img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * dark))))

_grad = {}
def gradient(img, side="left", strength=0.85, span=0.62):
    key = (side, strength, span)
    if key not in _grad:
        if side == "left":
            g = np.clip(1 - np.linspace(0, 1, W) / span, 0, 1) ** 1.3 * strength
            a = np.tile(g, (H, 1))
        else:
            g = np.clip((np.linspace(0, 1, H) - (1 - span)) / span, 0, 1) ** 1.2 * strength
            a = np.tile(g[:, None], (1, W))
        lay = np.zeros((H, W, 4), np.uint8); lay[..., :3] = [int(c * 0.25) for c in T["bg"]]; lay[..., 3] = (a * 255).astype(np.uint8)
        _grad[key] = Image.fromarray(lay, "RGBA")
    img.alpha_composite(_grad[key])

def credit(img, path, a=1.0):
    c = CREDITS.get(os.path.basename(path))
    if not c: return
    who = (c.get("artist") or c.get("credit") or "Wikimedia Commons").strip()
    h = len(who) // 2
    if len(who) % 2 == 0 and who[:h] == who[h:]: who = who[:h]          # Commons sometimes repeats the author
    s = f"Image: {who[:70]} · {c.get('license', '')} · via Wikimedia Commons"
    text_a(img, (W - 40, H - 66), s, F("inter", 17, "Medium"), (215, 215, 210), 0.85 * a, "rs", shadow=3)

def chip(img, x, y, s, col, a=1.0, size=40):
    f = F("anton", size); w = ImageDraw.Draw(img).textlength(s, font=f)
    rect_a(img, (x, y, x + w + 40, y + size + 26), col, a * 0.95, 14)
    text_a(img, (x + 20 + w / 2, y + (size + 26) / 2), s, f, WHITE, a, "mm")

# ---------------------------------------------------------------- scenes
def sc_clock(img, sc, t, D, tg, k):
    cx, cy, r = 560, 560, 330
    secs = sc.get("seconds", 85); m0 = sc.get("from_minutes", 3) * 60
    p = prog(t, 0.6, min(3.0, D * 0.45)); left = m0 + (secs - m0) * p        # seconds before midnight shown by the hand
    a = clamp(t / 0.5)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    pul = 0.5 + 0.5 * math.sin(tg * 4)
    gd.ellipse([cx - r - 40, cy - r - 40, cx + r + 40, cy + r + 40], fill=T["alert"] + (int(60 + 50 * pul * p),))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(50)))
    d = ImageDraw.Draw(img)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(14, 14, 14, int(240 * a)), outline=T["accent2"] + (int(255 * a),), width=6)
    # red danger sector: last 15 minutes before midnight
    d.pieslice([cx - r + 14, cy - r + 14, cx + r - 14, cy + r - 14], -90 - 90, -90, fill=T["alert"] + (int(70 * a),))
    for i in range(60):
        ang = math.radians(i * 6 - 90); L = 34 if i % 5 == 0 else 14; w = 7 if i % 5 == 0 else 3
        x0, y0 = cx + (r - 20) * math.cos(ang), cy + (r - 20) * math.sin(ang)
        x1, y1 = cx + (r - 20 - L) * math.cos(ang), cy + (r - 20 - L) * math.sin(ang)
        d.line([x0, y0, x1, y1], fill=WHITE + (int(220 * a),), width=w)
    ang_m = math.radians(-90 - left / 3600 * 360)                  # minute hand: N seconds before 12
    ang_h = math.radians(-90 - left / 43200 * 360)
    d.line([cx, cy, cx + (r * 0.55) * math.cos(ang_h), cy + (r * 0.55) * math.sin(ang_h)], fill=WHITE + (int(255 * a),), width=16)
    d.line([cx, cy, cx + (r * 0.84) * math.cos(ang_m), cy + (r * 0.84) * math.sin(ang_m)], fill=T["alert"] + (int(255 * a),), width=10)
    d.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=T["alert"] + (255,))
    # text
    mm, ss = int(left // 60), int(round(left % 60))
    if ss == 60: mm, ss = mm + 1, 0
    text_a(img, (1000, 330), "TIME TO MIDNIGHT", F("mono", 30), T["accent"], a)
    big_number(img, f"{mm:02d}:{ss:02d}", 996, 370, 220, T["alert"] if p > 0.95 else WHITE, a)
    ttl = sc.get("title", "")
    text_a(img, (1000, 650), typed(ttl, prog(t, 2.2, 1.2)), fit_font("disp", 64, ttl, W - 1060, "Black"), WHITE, 1, shadow=6)
    text_a(img, (1002, 740), sc.get("sub", ""), F("inter", 26, "Medium"), MUTED, prog(t, 3.0, 0.6))
    if sc.get("next"):                                            # teaser card for the next video
        st = max(3.0, D - 7.0); na = clamp((t - st) / 0.4); p2 = back(clamp((t - st) / 0.5))
        if na > 0:
            f = fit_font("disp", 40, sc["next"], 780, "Black")
            w = int(840 * clamp(p2, 0, 1.05))
            rect_a(img, (1000, 820, 1000 + w, 920), (230, 30, 40), na * 0.95, 20)
            text_a(img, (1030, 870), "▶  " + sc["next"], f, WHITE, clamp((t - st - 0.25) / 0.3), "lm")
    chrome(img, tg, clamp((t - 0.3) / 0.6))

def sc_image(img, sc, t, D, tg, k):
    kenburns(img, sc["img"], t, D, k, dark=0.18)
    gradient(img, "left", 0.92, 0.66); gradient(img, "bottom", 0.7, 0.45)
    y = 600 - 40 * len(sc.get("lines", []))
    x = 90
    if sc.get("code"):
        fl = flag(sc["code"], 120); paste_a(img, fl, (x, y - 170), prog(t, 0.2, 0.4))
    text_a(img, (x, y - 30), typed(sc.get("kicker", ""), prog(t, 0.2, 0.6)), F("mono", 30), T["accent"], 1, shadow=4)
    for i, ln in enumerate(sc.get("lines", [])):
        f = fit_font("disp", 72 if i == 0 else 52, ln, 1000, "Black" if i == 0 else "Bold")
        st = 0.6 + i * max(0.6, (D - 2.5) / max(1, len(sc["lines"])) * 0.6)
        text_a(img, (x, y + 30 + i * (92 if i == 0 else 74) + (0 if i == 0 else 18)), typed(ln, prog(t, st, 0.8)), f,
               WHITE if i == 0 else (230, 228, 220), 1, shadow=8)
    credit(img, sc["img"], clamp(t / 0.6))
    chrome(img, tg)

def sc_disclaimer(img, sc, t, D, tg, k):
    a = clamp(t / 0.5)
    rect_a(img, (260, 230, W - 260, H - 230), (10, 12, 12), 0.88 * a, 28, T["accent2"], 2)
    text_a(img, (320, 300), "ⓘ  PLEASE NOTE", F("disp", 46, "Black"), T["accent"], a)
    for i, ln in enumerate(sc.get("lines", [])):
        text_a(img, (324, 400 + i * 78), "•  " + ln, fit_font("inter", 32, "•  " + ln, W - 640, "Medium"), WHITE, prog(t, 0.5 + i * 0.5, 0.5))
    chrome(img, tg, a)

def sc_chapter(img, sc, t, D, tg, k):
    if sc.get("img"): kenburns(img, sc["img"], t, D, k, dark=0.55, blur=6)
    a = clamp(t / 0.4)
    w = int(900 * prog(t, 0.2, 0.7))
    rect_a(img, (120, 560, 120 + w, 566), T["accent"], a)
    text_a(img, (120, 470), f"CHAPTER {sc.get('n', '')}", F("mono", 40), T["accent"], prog(t, 0.1, 0.4), shadow=4)
    ttl = sc.get("title", "")
    text_a(img, (114, 590), typed(ttl, prog(t, 0.4, 0.7)), fit_font("disp", 130, ttl, W - 260, "Black"), WHITE, 1, shadow=10)
    chrome(img, tg, a, header=False)

def sc_timeline(img, sc, t, D, tg, k):
    pts = sc["points"]; x0, x1, y0, y1 = 200, W - 200, 860, 260
    ymin, ymax = 0, max(p[1] for p in pts) * 1.08
    def X(yr): return x0 + (yr - pts[0][0]) / (pts[-1][0] - pts[0][0]) * (x1 - x0)
    def Y(v): return y0 - (v - ymin) / (ymax - ymin) * (y0 - y1)
    a = clamp(t / 0.5)
    text_a(img, (x0, 170), sc.get("title", ""), F("disp", 48, "Black"), WHITE, a)
    d = ImageDraw.Draw(img)
    d.line([x0, y0, x1, y0], fill=MUTED + (int(200 * a),), width=2)
    for yr in range(1950, 2030, 10):
        d.line([X(yr), y0, X(yr), y0 + 10], fill=MUTED + (int(200 * a),), width=2)
        text_a(img, (X(yr), y0 + 34), str(yr), F("inter", 22, "Medium"), MUTED, a, "mm")
    p = prog(t, 0.6, max(2.0, D * 0.75)); xe = x0 + (x1 - x0) * p
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    seg = [(X(yr), Y(v)) for yr, v, _ in pts]
    poly = []
    for (xa, ya), (xb, yb) in zip(seg, seg[1:]):
        if xa > xe: break
        if xb > xe: yb = ya + (yb - ya) * (xe - xa) / (xb - xa); xb = xe
        poly += [(xa, ya), (xb, yb)]
    if len(poly) > 1:
        ld.polygon(poly + [(poly[-1][0], y0), (poly[0][0], y0)], fill=T["accent"] + (50,))
        ld.line(poly, fill=T["accent"] + (255,), width=7, joint="curve")
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(3))); img.alpha_composite(lay)
    for yr, v, lab in pts:
        if X(yr) <= xe + 1:
            d.ellipse([X(yr) - 11, Y(v) - 11, X(yr) + 11, Y(v) + 11], fill=T["alert"] + (255,))
            text_a(img, (X(yr), Y(v) - 30), lab, F("disp", 34, "Black"), WHITE, 1, "ms", shadow=5)
            text_a(img, (X(yr), Y(v) + 44), str(yr), F("mono", 22), T["accent"], 1, "mm")
    chrome(img, tg, a)

def sc_stat(img, sc, t, D, tg, k):
    g = GLOBE.render(25, 80 + tg * 3, dim_others=0.3)
    paste_a(img, g, (W - g.width * 0.78, H / 2 - g.height / 2), 0.35)
    a = clamp(t / 0.4)
    text_a(img, (120, 210), sc.get("kicker", ""), F("mono", 30), T["accent"], a)
    v = sc.get("value", 0); g2 = prog(t, 0.4, max(1.2, D * 0.3))
    s = sc.get("value_label") if (sc.get("value_label") and g2 > 0.98) or not v else f"{int(round(v * g2)):,}"
    big_number(img, s, 112, 250, 230, T["accent"] if v else T["alert"], a)
    text_a(img, (122, 540), sc.get("label", ""), fit_font("disp", 54, sc.get("label", ""), 1200, "Black"), WHITE, prog(t, 0.6, 0.5), shadow=6)
    if sc.get("note"): text_a(img, (124, 612), sc["note"], F("inter", 30, "Medium"), T["accent2"], prog(t, 1.0, 0.5))
    items = sc.get("items", [])
    for i, (b, s2) in enumerate(items):
        st = 1.2 + i * max(0.7, (D - 3) / max(1, len(items)) * 0.7); aa = prog(t, st, 0.4)
        x = 120 + i * 560; y = 700 + 30 * (1 - aa)
        rect_a(img, (x, y, x + 520, y + 220), (10, 12, 12), 0.86 * aa, 18, T["land_edge"], 2)
        text_a(img, (x + 30, y + 30), b, fit_font("anton", 72, b, 460), T["accent"], aa)
        text_a(img, (x + 30, y + 140), s2, fit_font("inter", 26, s2, 460, "SemiBold"), WHITE, aa)
    chrome(img, tg, a)

def sc_club(img, sc, t, D, tg, k):
    a = clamp(t / 0.4)
    text_a(img, (120, 150), sc.get("title", ""), F("disp", 56, "Black"), WHITE, a)
    text_a(img, (122, 222), sc.get("sub", ""), F("inter", 26, "Medium"), MUTED, a)
    rows = sc["rows"]; n = len(rows)
    for i, (code, name, yr) in enumerate(rows):
        st = 0.6 + i * (D - 2.0) / n; aa = prog(t, st, 0.4)
        cx, cy = i % 3, i // 3; x = 120 + cx * 570; y = 300 + cy * 220
        rect_a(img, (x, y, x + 540, y + 190), (10, 12, 12), 0.85 * max(aa, 0.35 * a), 18, T["accent"] if aa > 0 else T["land_edge"], 2)
        fl = flag(code, 120)
        if aa <= 0:
            paste_a(img, silhouette(fl), (x + 26, y + 95 - fl.height / 2), 0.6 * a)
            continue
        paste_a(img, fl, (x + 26, y + 95 - fl.height / 2), aa)
        text_a(img, (x + 176, y + 58), name, F("disp", 40, "Black"), WHITE, aa)
        text_a(img, (x + 176, y + 118), yr, fit_font("anton", 50, yr, 340), T["accent"], aa)
    chrome(img, tg, a)

def sc_country(img, sc, t, D, tg, k):
    code = sc["code"]; la, lo = CENTROID.get(code, (20, 70)); la = max(-45, min(45, la))
    m = ease_io(t / 1.4); lat = 15 + (la - 15) * m; lon = (lo - 40) + 40 * m + t * 1.2
    reveal = sc.get("reveal_at", 0.9); shown = t >= reveal
    g = GLOBE.render(lat, lon, highlight=[code] if shown else None, hl_alpha=prog(t, reveal, 0.4), dim_others=0.35,
                     pulse=0.5 + 0.5 * math.sin(tg * 5))
    gx, gy = 560 - g.width / 2, 560 - g.height / 2; paste_a(img, g, (gx, gy), 1)
    (px, py), vis = GLOBE.point(la, lo, lat, lon)
    if vis > 0:
        d = ImageDraw.Draw(img)
        for j in range(3):
            ph = (tg * 0.7 + j / 3) % 1; rr = 20 + ph * 90
            d.ellipse([gx + px - rr, gy + py - rr, gx + px + rr, gy + py + rr], outline=T["accent"] + (int(200 * (1 - ph)),), width=3)
    x = 1060; a = clamp(t / 0.4)
    rect_a(img, (x - 40, 200, W - 80, 920), (10, 12, 12), 0.84 * a, 24, T["land_edge"], 2)
    fl = flag(code, 150)
    if shown:
        s = 1 + 0.25 * (1 - ease((t - reveal) / 0.4)); f2 = fl.resize((int(fl.width * s), int(fl.height * s)))
        paste_a(img, f2, (x + (fl.width - f2.width) / 2, 250 + (fl.height - f2.height) / 2), clamp((t - reveal) / 0.15))
        text_a(img, (x + 180, 262), typed(sc.get("name", ""), prog(t, reveal, 0.5)), fit_font("disp", 76, sc.get("name", ""), 600, "Black"), WHITE, 1, shadow=5)
    else:
        paste_a(img, silhouette(fl), (x, 250), a)
    na = prog(t, reveal + 0.3, 0.4)
    y0s, y1s = sc.get("y0", ""), sc.get("y1", "")
    text_a(img, (x, 440), y0s, F("mono", 30), MUTED, na)
    fl_s = sc.get("from_label") or f"{sc['from']:,}"
    fw = ImageDraw.Draw(img).textlength(fl_s, font=F("anton", 96))
    text_a(img, (x, 480), fl_s, F("anton", 96), MUTED, na)
    text_a(img, (x + fw + 24, 520), "→", F("disp", 70, "Black"), T["accent2"], na)
    g2 = prog(t, reveal + 0.6, max(1.0, D * 0.25)); cur = int(round(sc["from"] + (sc["to"] - sc["from"]) * g2))
    big_number(img, f"{cur:,}", x + fw + 110, 456, 140, T["accent"], na)
    text_a(img, (x + fw + 110, 440), y1s, F("mono", 30), T["accent"], na)
    if sc.get("chip"): chip(img, W - 330, 470, sc["chip"], T["alert"], prog(t, reveal + 1.2, 0.3), 44)
    for i, ln in enumerate(sc.get("facts", [])):
        text_a(img, (x, 690 + i * 60), "▸ " + typed(ln, prog(t, reveal + 1.4 + i * 0.8, 0.8)), fit_font("inter", 32, "▸ " + ln, 760, "SemiBold"), T["accent2"], prog(t, reveal + 1.4 + i * 0.8, 0.3))
    chrome(img, tg, a)

_silo_globe = {}
def sc_silos(img, sc, t, D, tg, k):
    lat0, lon0 = 38.0, 100.0
    if k not in _silo_globe:
        G = R.Globe(1250); _silo_globe[k] = (G, G.render(lat0, lon0, highlight=["CN"], hl_alpha=0.35, dim_others=0.2))
    G, gim = _silo_globe[k]
    z = 1.0 + 0.18 * ease_io(t / D)
    cx, cy = G.point(40.8, 99.5, lat0, lon0)[0]                      # frame centred between the three fields
    cw, ch = W / z, H / z
    crop = gim.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize((W, H), Image.BILINEAR)
    img.alpha_composite(crop)
    img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 70)))
    d = ImageDraw.Draw(img)
    def to_screen(la, lo):
        (px, py), _ = G.point(la, lo, lat0, lon0)
        return (px - (cx - cw / 2)) * z, (py - (cy - ch / 2)) * z
    fields = sc["fields"]
    for i, fld in enumerate(fields):
        name, la, lo, lab = fld[:4]; side = fld[4] if len(fld) > 4 else "right"
        st = 1.5 + i * max(1.2, (D - 4) / len(fields)); aa = prog(t, st, 0.5)
        if aa <= 0: continue
        sx, sy = to_screen(la, lo)
        for gx in range(-4, 5):                                       # a grid of "silo" dots, like the satellite pictures
            for gy in range(-3, 4):
                if (gx * 7 + gy * 3) % 5 == 0: continue
                px, py = sx + gx * 8, sy + gy * 8
                d.rectangle([px - 2, py - 2, px + 2, py + 2], fill=T["alert"] + (int(230 * aa),))
        for j in range(2):
            ph = (tg * 0.6 + j / 2) % 1; rr = 44 + ph * 60
            d.ellipse([sx - rr, sy - rr, sx + rr, sy + rr], outline=T["accent"] + (int(200 * (1 - ph) * aa),), width=3)
        if side == "below": lx, ly, anc = sx, sy + 70, "ma"
        elif side == "right": lx, ly, anc = sx + 80, sy - 50, "la"
        else: lx, ly, anc = sx - 80, sy - 90, "ra"
        text_a(img, (lx, ly), name.upper(), F("disp", 40, "Black"), WHITE, aa, anc, shadow=6)
        text_a(img, (lx, ly + 52), lab + " silos", F("anton", 46), T["accent"], aa, anc, shadow=6)
    a = clamp(t / 0.4)
    text_a(img, (90, 150), sc.get("title", ""), F("disp", 60, "Black"), WHITE, a, shadow=8)
    text_a(img, (92, 226), "Probable missile-silo fields identified on commercial satellite images (FAS / CNS)", F("inter", 24, "Medium"), MUTED, a, shadow=4)
    if sc.get("total"):
        tt = 1.5 + len(fields) * max(1.2, (D - 4) / len(fields))
        chip(img, 90, H - 230, sc["total"], T["alert"], prog(t, tt, 0.4), 60)
    chrome(img, tg, a)

def sc_compare(img, sc, t, D, tg, k):
    a = clamp(t / 0.4)
    text_a(img, (120, 160), sc.get("title", ""), F("disp", 64, "Black"), WHITE, a)
    text_a(img, (122, 244), sc.get("sub", ""), F("inter", 26, "Medium"), MUTED, a)
    rows = sc["rows"]; vmax = max(max(r[2], r[3]) for r in rows) * 1.1
    y0, x0, xw = 360, 520, W - 520 - 300
    ys = sc.get("years", ["", ""])
    text_a(img, (x0, y0 - 36), "■ " + ys[0], F("mono", 26), MUTED, a); text_a(img, (x0 + 200, y0 - 36), "■ " + ys[1], F("mono", 26), T["accent"], a)
    for i, (code, name, v0, v1) in enumerate(rows):
        y = y0 + i * 270; aa = prog(t, 0.4 + i * 0.4, 0.4)
        fl = flag(code, 120); paste_a(img, fl, (120, y + 40), aa)
        text_a(img, (260, y + 70), name, F("disp", 48, "Black"), WHITE, aa)
        p0 = prog(t, 0.8 + i * 0.4, 1.0); p1 = prog(t, max(1.8, D * 0.35) + i * 0.6, 1.4)
        w0, w1 = xw * v0 / vmax * p0, xw * v1 / vmax * p1
        rect_a(img, (x0, y + 20, x0 + max(w0, 1), y + 90), MUTED, 0.55 * aa, 10)
        text_a(img, (x0 + w0 + 20, y + 55), f"{int(v0 * p0):,}", F("anton", 46), MUTED, aa, "lm")
        rect_a(img, (x0, y + 110, x0 + max(w1, 1), y + 180), T["accent"], 0.95 * aa, 10)
        if p1 > 0: text_a(img, (x0 + w1 + 20, y + 145), f"{int(v1 * p1):,}", F("anton", 52), T["accent"], aa, "lm")
    chrome(img, tg, a)

def sc_events(img, sc, t, D, tg, k):
    a = clamp(t / 0.4)
    text_a(img, (120, 170), sc.get("title", ""), F("disp", 56, "Black"), WHITE, a)
    ev = sc["events"]; n = len(ev); x0, x1, y = 160, W - 160, 560
    p = prog(t, 0.4, D * 0.85)
    rect_a(img, (x0, y - 3, x0 + (x1 - x0) * p, y + 3), T["accent2"], a)
    for i, (yr, name, sub) in enumerate(ev):
        x = x0 + (x1 - x0) * i / (n - 1); st = 0.4 + D * 0.85 * i / (n - 1); aa = prog(t, st, 0.4)
        if aa <= 0: continue
        last = i == n - 1
        col = T["alert"] if last or "end" in name.lower() or "suspend" in name.lower() else T["accent"]
        ImageDraw.Draw(img).ellipse([x - 16, y - 16, x + 16, y + 16], fill=col + (int(255 * aa),))
        up = i % 2 == 0
        text_a(img, (x, y - 70 if up else y + 70), yr, F("anton", 54), col, aa, "mm")
        text_a(img, (x, y - 140 if up else y + 140), name, fit_font("disp", 32, name, 300, "Black"), WHITE, aa, "mm")
        if sub: text_a(img, (x, y - 182 if up else y + 182), sub, fit_font("inter", 22, sub, 300, "Medium"), MUTED, aa, "mm")
    chrome(img, tg, a)

def sc_bars(img, sc, t, D, tg, k):
    a = clamp(t / 0.4)
    text_a(img, (120, 140), sc.get("title", ""), F("disp", 56, "Black"), WHITE, a)
    text_a(img, (122, 212), sc.get("sub", ""), F("inter", 24, "Medium"), MUTED, a)
    rows = sc["rows"]; vmax = max(r[2] for r in rows); x0, xw = 520, W - 520 - 260
    rh = min(84, int(700 / len(rows)))
    for i, (code, name, v) in enumerate(rows):
        y = 270 + i * rh; st = 0.5 + i * (D * 0.5) / len(rows); aa = prog(t, st, 0.4); p = prog(t, st, 1.0)
        fl = flag(code, int(rh * 0.8)); paste_a(img, fl, (120, y + (rh - fl.height) / 2), aa)
        text_a(img, (130 + fl.width + 20, y + rh / 2), name, F("disp", 34, "Bold"), WHITE, aa, "lm")
        w = max(4, xw * v / vmax * p)
        rect_a(img, (x0, y + 12, x0 + w, y + rh - 12), T["accent"] if i > 1 else T["alert"], 0.92 * aa, 8)
        text_a(img, (x0 + w + 16, y + rh / 2), f"{int(v * p):,}", F("anton", 40), WHITE, aa, "lm")
    chrome(img, tg, a)

def sc_outro(img, sc, t, D, tg, k):
    g = GLOBE.render(22, 78 + t * 3, dim_others=0.25)
    paste_a(img, g, (W - g.width + 40, H / 2 - g.height / 2), 0.55)
    a = clamp(t / 0.5)
    for i, ln in enumerate(sc.get("lines", [])):
        text_a(img, (120, 260 + i * 100), typed(ln, prog(t, 0.4 + i * 1.0, 0.9)), fit_font("disp", 72 if i == 0 else 54, ln, 1100, "Black"),
               WHITE if i == 0 else T["accent"], 1, shadow=8)
    st = max(1.5, D - 7.0); p = back(clamp((t - st) / 0.5)); aa = clamp((t - st) / 0.3)
    if aa > 0:
        rect_a(img, (120, 620, 120 + int(980 * clamp(p, 0, 1.06)), 900), (10, 10, 12), 0.92 * aa, 26, T["accent"], 3)
        paste_a(img, R.LOGO.resize((150, 150), Image.LANCZOS), (160, 685), aa)
        text_a(img, (340, 700), "UNKNOWN UNCOVERED", F("disp", 52, "Black"), WHITE, aa)
        text_a(img, (342, 768), "@Unknown_Uncovered_2026", F("inter", 28, "SemiBold"), T["accent2"], aa)
        rect_a(img, (340, 820, 640, 878), (230, 30, 40), aa, 29)
        text_a(img, (490, 849), "SUBSCRIBE", F("disp", 32, "Black"), WHITE, clamp((t - st - 0.3) / 0.2), "mm")
        text_a(img, (670, 849), "LIKE   ·   COMMENT   ·   SHARE", F("inter", 28, "SemiBold"), WHITE, clamp((t - st - 0.5) / 0.3), "lm")
    chrome(img, tg, a)

def sc_counter(img, sc, t, D, tg, k):
    """Cold open: big counter that rolls from `from` (year y0) to `to` (year y1); only real years shown."""
    g = GLOBE.render(30, 40 + tg * 4, dim_others=0.3)
    paste_a(img, g, (W - g.width * 0.62, H / 2 - g.height / 2), 0.38)
    p = prog(t, 1.2, max(2.5, D * 0.5))
    y0s, y1s = str(sc.get("y0", "")), str(sc.get("y1", ""))
    y = y0s if p <= 0.0 else (y1s if p > 0.98 else f"{y0s}  →  {y1s}")
    v = sc["to"] if p > 0.98 else int(round(sc["from"] + (sc["to"] - sc["from"]) * ease_io(p)))
    a = clamp(t / 0.5)
    text_a(img, (140, 230), y, F("anton", 96), T["accent"], a, shadow=8)
    big_number(img, f"{v:,}", 128, 350, 300, WHITE if p < 0.98 else T["accent"], a)
    text_a(img, (142, 720), sc.get("label", ""), fit_font("disp", 54, sc.get("label", ""), 1300, "Black"), MUTED, a, shadow=6)
    bw = (W - 280) * (v / max(sc["from"], sc["to"]))
    rect_a(img, (140, 820, W - 140, 856), (40, 40, 40), 0.9 * a, 18)
    rect_a(img, (140, 820, 140 + bw, 856), T["alert"] if p > 0.5 else T["accent"], a, 18)
    if sc.get("chip") and p > 0.98:
        ca = clamp((t - 1.2 - max(2.5, D * 0.5)) / 0.3)
        chip(img, 140, 890, sc["chip"] + "  WEAPONS GONE", T["alert"], ca, 56)
    chrome(img, tg, a)

def _bomb(d, cx, cy, s, col):
    d.rounded_rectangle([cx - 90 * s, cy - 220 * s, cx + 90 * s, cy + 160 * s], radius=int(90 * s), outline=col, width=int(12 * s))
    for sx in (-1, 1):
        d.polygon([(cx + sx * 60 * s, cy + 140 * s), (cx + sx * 150 * s, cy + 280 * s), (cx + sx * 40 * s, cy + 250 * s)], outline=col, width=int(10 * s))
    d.line([cx, cy + 160 * s, cx, cy + 270 * s], fill=col, width=int(10 * s))

def _bulb(d, cx, cy, s, col):
    d.ellipse([cx - 150 * s, cy - 260 * s, cx + 150 * s, cy + 40 * s], outline=col, width=int(12 * s))
    for sx in (-70, 70): d.line([cx + sx * s, cy + 30 * s, cx + sx * s, cy + 130 * s], fill=col, width=int(12 * s))
    for i in range(3):
        yy = cy + (140 + i * 34) * s; d.line([cx - 75 * s, yy, cx + 75 * s, yy], fill=col, width=int(12 * s))
    d.line([cx - 40 * s, cy - 40 * s, cx - 15 * s, cy - 120 * s, cx + 15 * s, cy - 40 * s, cx + 40 * s, cy - 120 * s], fill=col, width=int(8 * s))

def sc_bulb(img, sc, t, D, tg, k):
    """Bomb outline morphs into a glowing bulb (right), text on the left."""
    cx, cy = 1400, 560
    m = ease_io(clamp((t - 1.5) / 2.0))
    if m > 0.3:
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse([cx - 300, cy - 420, cx + 300, cy + 160], fill=(255, 214, 90, int(170 * (m - 0.3) / 0.7)))
        img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(70)))
    la = Image.new("RGBA", (W, H), (0, 0, 0, 0)); _bomb(ImageDraw.Draw(la), cx, cy - 40, 1.1, T["alert"] + (255,))
    lb = Image.new("RGBA", (W, H), (0, 0, 0, 0)); _bulb(ImageDraw.Draw(lb), cx, cy + 40, 1.1, (255, 222, 120, 255))
    paste_a(img, la, (0, 0), (1 - m) * clamp(t / 0.4)); paste_a(img, lb, (0, 0), m)
    if 0.05 < m < 0.95:
        r = np.random.default_rng(int(tg * 100)); dd = ImageDraw.Draw(img)
        for _ in range(40):
            an = r.uniform(0, 6.28); rr = r.uniform(100, 340) * m
            dd.ellipse([cx + rr * math.cos(an) - 4, cy + rr * math.sin(an) - 4, cx + rr * math.cos(an) + 4, cy + rr * math.sin(an) + 4], fill=(255, 230, 150, 220))
    a = clamp(t / 0.4)
    text_a(img, (120, 300), typed(sc.get("kicker", ""), prog(t, 0.2, 0.6)), F("mono", 30), T["accent"], 1, shadow=4)
    big_number(img, sc.get("big", ""), 110, 350, 230, (255, 222, 120), prog(t, 2.5, 0.5))
    for i, ln in enumerate(sc.get("lines", [])):
        text_a(img, (122, 640 + i * 70), typed(ln, prog(t, 3.0 + i * 0.8, 0.8)), fit_font("disp", 52, ln, 1000, "Black" if i == 0 else "Bold"), WHITE, 1, shadow=6)
    chrome(img, tg, a)

R.SCENE_FN.update({"counter": sc_counter, "bulb": sc_bulb})
R.SCENE_FN.update({"clock": sc_clock, "image": sc_image, "disclaimer": sc_disclaimer, "chapter": sc_chapter, "timeline": sc_timeline,
                   "stat": sc_stat, "club": sc_club, "country": sc_country, "silos": sc_silos, "compare": sc_compare,
                   "events": sc_events, "bars": sc_bars, "outro": sc_outro})

# ---------------------------------------------------------------- passport scenes (reel 012), 16:9 versions of uu_story's
import uu_story as S

def left_text(img, sc, t, D, y=330, w=760):
    """Kicker, big headline and rising lines in the left column (x=120)."""
    text_a(img, (120, y), typed(sc.get("kicker", ""), prog(t, 0.2, 0.6)), F("mono", 30), T["accent"], 1, shadow=4)
    yy = y + 60
    if sc.get("big"):
        g = back(clamp((t - 0.5) / 0.5)); b = sc["big"]
        f = fit_font("anton", int(150 * (0.85 + 0.15 * clamp(g, 0, 1.2))), b, w)
        text_a(img, (114, yy), b, f, WHITE, clamp((t - 0.5) / 0.25), shadow=10); yy += 190
    for i, ln in enumerate(sc.get("lines", [])):
        st = 1.0 + i * 0.8; f = fit_font("disp", 52 if i == 0 else 44, ln, w, "Black" if i == 0 else "Bold")
        x = 120
        S.rise_line(img, ln, x + ImageDraw.Draw(img).textlength(ln, font=f) / 2, yy + 30 + i * 72, f, t - st,
                    WHITE if i == 0 else (225, 222, 212))

def sc_booklet_l(img, sc, t, D, tg, k):
    a = S.draw_booklet(img, sc, t, sc.get("cx", 1330), sc.get("y", 250))
    left_text(img, sc, t, D)
    chrome(img, tg, a)

EU_L = dict(c_lat=48.0, c_lon=7.0, s=34.0, cx=1330, cy=560)
def sc_borders_l(img, sc, t, D, tg, k):
    a = clamp(t / 0.5); la_ = sc.get("lock_at", 1.6)
    before = S.draw_borders(img, sc, t, tg, a, EU_L)
    yr = "1913" if before else "1914"
    text_a(img, (120, 230), yr, F("anton", 190), T["accent"] if before else T["alert"], a, shadow=10)
    lab = "FREE TO TRAVEL" if before else "PASSPORT REQUIRED"
    f = F("anton", 70); w = ImageDraw.Draw(img).textlength(lab, font=f); pa = 1.0 if before else ease(clamp((t - la_) / 0.3))
    rect_a(img, (120, 500, 120 + w + 60, 600), (T["accent2"] if before else T["alert"]), 0.92 * a * pa, 16)
    text_a(img, (150 + w / 2, 550), lab, f, (14, 10, 6), a * pa, "mm")
    for i, ln in enumerate(sc.get("lines", [])):
        base = la_ if la_ < D else 0.4                                # map with no lock (lock_at beyond the scene): lines come early
        st = base + 0.6 + i * (max(0.8, sc.get("follow_at", 4.5) - la_ - 0.6) if la_ < D else 1.2)
        ff = fit_font("disp", 46, ln, 700, "Bold")
        S.rise_line(img, ln, 120 + ImageDraw.Draw(img).textlength(ln, font=ff) / 2, 680 + i * 70, ff, t - st)
    chrome(img, tg, a)

def sc_dossier_l(img, sc, t, D, tg, k):
    a = S.draw_dossier(img, sc, t, x0=sc.get("x0", 960), y0=sc.get("y0", 200))
    left_text(img, sc, t, D, y=360, w=760)
    if sc.get("img"): credit(img, sc["img"], a)
    chrome(img, tg, a)

R.SCENE_FN.update({"booklet": sc_booklet_l, "borders": sc_borders_l, "dossier": sc_dossier_l})
R.SCENE_FN.update({"counter": sc_counter, "bulb": sc_bulb, "timeline": sc_timeline})   # uu_story registers vertical versions of these

if __name__ == "__main__":
    R.main()
