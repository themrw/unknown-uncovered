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
  fingerprint {seed, scan_at, search_at, match_at, left_label, right_label, stamp, kicker, big, lines}  evidence + record search (match_at past the scene = cliffhanger)
  drawers    {kicker, whorls, finger_at, formula_at, drawer_at, lines}  Haque-Bose formula + 1,024-drawer grid
  spread     {origin, year0, routes, kicker, lines}                   arcs over a world map
  cartoon    {bg: drawers|board|glow, board[], card, glass, kicker, big, lines}  the two cartoon sub-inspectors (uu_cartoon.py), text left
  patterns   {kicker, show_at[3], count_at, whorl_at, lines, lines_at}  arch / loop / whorl + 'check your thumb' countdown
  versus     {kicker, left, right, rows[[label, left, right]], row_at, win_at, stamp, lines}  head-to-head comparison
  duel       {kicker, big, big_label, rows[[label, value, text]], mystery[3], card_at[3]}  premise counter + bars + 3 hidden 'characters'
  stall      {props: coins|qr|soundbox|photo, photo_at, kicker, big, lines}   Raju's tea stall (fictional cartoon), text left
  paynet     {banks[5], apps[5], hub, link_at, address, addr_at, kicker, lines}  banks <-> UPI <-> apps network, text left
  jio        {p0, p1, price_at, kicker, lines}                         people pouring in, then the price of 1 GB collapsing
  qrtown     {img, town_at, chip0, chip1, chip, chip_at, kicker, lines} note-ban photo, then a town where QR stickers pop
  walletpipe {split[2], split_at, kicker, lines}                       wallet lane vs direct UPI lane + split bar
  soundbox   {say, chart[[label, bn]], chart_at, kicker, lines}         talking box with a Hindi bubble + first-billion chart
  festive    {img, value, unit, label, items[[big, small]], items_at}  record month over a festive photo
  growth     {v0, v1, y0, y1, unit, grow_at, duel[[label, value]], duel_label, visa_at, kicker}  ten-year counter + UPI vs Visa
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

# ---------------------------------------------------------------- fingerprint scenes (reel 014), 16:9
def sc_fingerprint_l(img, sc, t, D, tg, k):
    a = S.draw_fingerprint(img, sc, t, sc.get("xl", 880), sc.get("xr", 1400), sc.get("y", 210))
    left_text(img, sc, t, D, y=380, w=680)
    chrome(img, tg, a)

def sc_drawers_l(img, sc, t, D, tg, k):
    """16:9 Haque-Bose primary classification: finger tiles + fraction on the left, 1,024-drawer grid on the right."""
    a = clamp(t / 0.4); d = ImageDraw.Draw(img)
    text_a(img, (110, 170), typed(sc.get("kicker", ""), prog(t, 0.1, 0.6)), F("mono", 30), T["accent"], 1, shadow=4)
    wh = sc.get("whorls", [1, 4, 7]); fat = sc.get("finger_at", [1.0 + i * 0.6 for i in range(len(wh))])
    tw_, gap, x0 = 160, 14, 110
    for i in range(10):
        r_, c_ = divmod(i, 5); x = x0 + c_ * (tw_ + gap); y = 220 + r_ * 200; ap = clamp((t - 0.2 - i * 0.05) / 0.3) * a
        n = i + 1; on = n in wh and t >= fat[wh.index(n)]; col = T["accent"] if on else (60, 80, 86)
        rect_a(img, (x, y, x + tw_, y + 186), (14, 24, 28), 0.9 * ap, 12)
        d.rounded_rectangle([x, y, x + tw_, y + 186], 12, outline=col + (int(255 * ap),), width=3 if on else 2)
        img.alpha_composite(S.fp_img(90, 114, 30 + i, (WHITE if on else (110, 120, 120)), (1.0 if on else 0.5) * ap, "whorl" if n in wh else "arch"), (int(x + (tw_ - 90) / 2), int(y + 28)))
        text_a(img, (x + tw_ / 2, y + 15), S.FNAME[i], F("mono", 16), MUTED, ap, "mm")
        text_a(img, (x + tw_ / 2, y + 164), f"{S.FVAL[i]}" if on else "0", F("anton", 36), T["accent2"] if on else (90, 100, 100), ap, "mm")
    fa = sc.get("formula_at", fat[-1] + 0.8); fp = ease(clamp((t - fa) / 0.6))
    num = [S.FVAL[n - 1] for n in wh if n % 2 == 0]; den = [S.FVAL[n - 1] for n in wh if n % 2 == 1]; N, Dn = 1 + sum(num), 1 + sum(den)
    if fp > 0:
        text_a(img, (300, 700), " + ".join(["1"] + [str(v) for v in num]), F("anton", 56), WHITE, fp, "mm", shadow=6)
        rect_a(img, (130, 738, 470, 744), T["accent"], fp)
        text_a(img, (300, 782), " + ".join(["1"] + [str(v) for v in den]), F("anton", 56), WHITE, fp, "mm", shadow=6)
        text_a(img, (540, 742), "=", F("anton", 86), MUTED, fp, "mm")
        text_a(img, (740, 742), f"{N}/{Dn}", F("anton", 150), T["accent2"], fp, "mm", shadow=10)
    ga = ease(clamp((t - fa - 0.6) / 0.8)); da = sc.get("drawer_at", fa + 2.2)
    if ga > 0:
        cs, cg = 16, 2; gx, gy = 1180, 230
        text_a(img, (gx + 16 * (cs + cg), gy - 40), "32 × 32 = 1,024 DRAWERS", F("mono", 30), T["accent"], ga, "mm")
        hr, hc = Dn - 1, N - 1; op = ease(clamp((t - da) / 0.5))
        for rr_ in range(32):
            for cc in range(32):
                if (rr_ + cc) / 62 > ga: continue
                xx, yy = gx + cc * (cs + cg), gy + rr_ * (cs + cg); hit = (rr_ == hr and cc == hc)
                fill = (T["accent2"] + (255,)) if (hit and op > 0) else (70, 130, 138, 255) if (rr_ == hr or cc == hc) and op > 0 else (40, 72, 80, 255)
                d.rectangle([xx, yy, xx + cs, yy + cs], fill=fill)
        if op > 0:
            xx, yy = gx + hc * (cs + cg) + cs / 2, gy + hr * (cs + cg) + cs / 2
            rr = 16 + 10 * math.sin(tg * 6); d.ellipse([xx - rr, yy - rr, xx + rr, yy + rr], outline=T["accent2"] + (255,), width=3)
            text_a(img, (xx + 34, yy - 4), f"DRAWER {N}/{Dn}", F("mono", 28), T["accent2"], op, "lm", shadow=6)
    for i, ln in enumerate(sc.get("lines", [])):
        f = fit_font("disp", 44 if i == 0 else 38, ln, 900, "Black" if i == 0 else "Bold")
        S.rise_line(img, ln, 110 + ImageDraw.Draw(img).textlength(ln, font=f) / 2, 880 + i * 60, f, t - (da + 0.4 + i * 0.6))
    chrome(img, tg, a)

def sc_spread_l(img, sc, t, D, tg, k):
    a = clamp(t / 0.5)
    S.WD.update(c_lat=12.0, c_lon=30.0, s=5.0, cx=1250, cy=560)
    year = S.draw_spread(img, sc, t, tg, a)
    text_a(img, (110, 250), year, F("anton", 150), T["accent2"], a, shadow=10)
    left_text(img, dict(sc, big=None), t, D, y=470, w=520)
    chrome(img, tg, a)

R.SCENE_FN.update({"fingerprint": sc_fingerprint_l, "drawers": sc_drawers_l, "spread": sc_spread_l})

# ---------------------------------------------------------------- reel 014b: cartoon officers, patterns, versus (16:9)
import uu_cartoon
_cart = {}
def sc_cartoon(img, sc, t, D, tg, k):
    """The two cartoon sub-inspectors on the right (bg: drawers | board | glow), text on the left."""
    a = ease(clamp(t / 0.6)); bgk = sc.get("bg", "drawers"); d = ImageDraw.Draw(img)
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse([900, 40, 1800, 1000], fill=(30, 170, 175, int(150 * a)))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(140)))
    if bgk in ("drawers", "glow"):
        fp = S.fp_img(640, 820, 7, T["accent"], 0.4 * a); img.alpha_composite(fp, (1110, 80))
    if bgk == "drawers":
        for r in range(11):
            for c in range(2):
                x0, y0 = W - (c + 1) * 92, 40 + r * 92
                d.rectangle([x0, y0, x0 + 84, y0 + 84], fill=(16, 34, 40, int(235 * a)), outline=(60, 120, 125, int(255 * a)), width=2)
                d.rectangle([x0 + 30, y0 + 36, x0 + 54, y0 + 44], fill=(255, 196, 96, int(200 * a)))
                d.text((x0 + 42, y0 + 18), f"{(r * 3 + c) % 32 + 1}/{(r + 5 * c) % 32 + 1}", font=F("mono", 14), fill=(120, 170, 170, int(200 * a)), anchor="mm")
    if bgk == "board":
        rect_a(img, (90, 90, 960, 500), (26, 52, 40), 0.96 * a, 10); d = ImageDraw.Draw(img)
        d.rectangle([90, 90, 960, 500], outline=(120, 90, 50, int(255 * a)), width=12)
        chalk = (232, 236, 226)
        for i, ln in enumerate(sc.get("board", ["16 · 8 · 4 · 2 · 1", "1 + 8  /  1 + 16 + 2", "= 9/19  →  drawer"])):
            text_a(img, (140, 150 + i * 110), typed(ln, prog(t, 0.6 + i * 0.8, 0.8)), fit_font("disp", 64, ln, 780, "Bold"), chalk, a, shadow=0)
    key = (sc.get("card", True), sc.get("glass", True))
    if key not in _cart:
        _cart[key] = uu_cartoon.officers_layer(W, H, 1240, 1620, 1040, 1050, 9.0, 9.4, card=key[0], glass=key[1], fp_img=S.fp_img)
    bob = 5 * math.sin(tg * 2.2); slide = (1 - a) * 160
    paste_a(img, _cart[key], (slide, bob), a)
    if key[0]:                                                            # card glow pulse
        gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); cx_, cy_ = 1240 + 19 * 9.0 + slide, 1040 - 50 * 9.0 + bob
        ImageDraw.Draw(gl).ellipse([cx_ - 40, cy_ - 150, cx_ + 210, cy_ + 30], fill=(255, 240, 200, int((40 + 30 * math.sin(tg * 3)) * a)))
        img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(40)))
    left_text(img, sc, t, D, y=sc.get("ty", 590 if bgk == "board" else 330), w=760)
    text_a(img, (W - 24, H - 60), "Illustration · not actual likeness", F("inter", 18), (150, 170, 170), 0.8 * a, "rm")
    chrome(img, tg, a)

def sc_patterns(img, sc, t, D, tg, k):
    """Arch, loop, whorl side by side; then 'check your thumb' countdown; whorl highlighted."""
    a = clamp(t / 0.4); d = ImageDraw.Draw(img)
    text_a(img, (W / 2, 150), typed(sc.get("kicker", "LOOK AT YOUR THUMB"), prog(t, 0.1, 0.6)), F("mono", 34), T["accent"], 1, "mm", shadow=4)
    kinds = [("arch", "ARCH", "मेहराब"), ("loop", "LOOP", "लूप"), ("whorl", "WHORL", "भँवर")]
    ats = sc.get("show_at", [0.6, 1.6, 2.6]); wa = sc.get("whorl_at", ats[-1] + 1.5)
    for i, (kd, en, hi) in enumerate(kinds):
        p = ease(clamp((t - ats[i]) / 0.6))
        if p <= 0: continue
        cx = W / 2 + (i - 1) * 440; y0 = 230 + (1 - p) * 60; hot = kd == "whorl" and t >= wa
        rect_a(img, (cx - 170, y0, cx + 170, y0 + 520), (14, 26, 30), 0.92 * p, 18)
        d.rounded_rectangle([cx - 170, y0, cx + 170, y0 + 520], 18, outline=(T["accent2"] if hot else (70, 120, 126)) + (int(255 * p),), width=5 if hot else 2)
        img.alpha_composite(S.fp_img(260, 340, 60 + i, (WHITE if (hot or kd != "whorl") else (225, 235, 235)), 0.95 * p, kd), (int(cx - 130), int(y0 + 30)))
        text_a(img, (cx, y0 + 410), en, F("anton", 64), T["accent2"] if hot else WHITE, p, "mm", shadow=6)
        text_a(img, (cx, y0 + 475), hi, F("hindi", 44), MUTED, p, "mm")
        if hot:
            q = ease(clamp((t - wa) / 0.4)); rr = 30 + 20 * math.sin(tg * 5)
            text_a(img, (cx, y0 - 40), "= 16 · 8 · 4 · 2 · 1", F("mono", 30), T["accent2"], q, "mm", shadow=6)
    ca = sc.get("count_at")
    if ca is not None and ca <= t < ca + 3.2:
        n = 3 - int(t - ca); q = 1 - ((t - ca) % 1.0)
        text_a(img, (W / 2, 900), f"CHECK YOUR THUMB  ·  {n}", F("anton", 70), T["accent2"], min(1, q * 1.6), "mm", shadow=10)
    for i, ln in enumerate(sc.get("lines", [])):
        f = fit_font("disp", 44, ln, 1500, "Bold"); S.rise_line(img, ln, W / 2, 900 + i * 62, f, t - sc.get("lines_at", D - 3) - i * 0.6)
    chrome(img, tg, a)

def sc_versus(img, sc, t, D, tg, k):
    """Head-to-head: body measurements vs fingerprints, rows revealed with ✗ / ✓, then a WINNER stamp."""
    a = clamp(t / 0.4); d = ImageDraw.Draw(img)
    text_a(img, (W / 2, 140), typed(sc.get("kicker", ""), prog(t, 0.1, 0.6)), F("mono", 32), T["accent"], 1, "mm", shadow=4)
    cols = [(560, sc.get("left", "BODY MEASUREMENTS"), T["alert"]), (1360, sc.get("right", "FINGERPRINTS"), (60, 220, 140))]
    for cx, title, col in cols:
        rect_a(img, (cx - 360, 210, cx + 360, 880), (14, 24, 28), 0.9 * a, 18)
        text_a(img, (cx, 270), title, fit_font("anton", 66, title, 660), WHITE, a, "mm", shadow=6)
    text_a(img, (W / 2, 560), "VS", F("anton", 120), T["accent2"], a, "mm", shadow=12)
    rows = sc.get("rows", [["COST", "EXPENSIVE", "CHEAP"], ["SPEED", "SLOW", "FAST"], ["ACCURACY", "ERROR-PRONE", "MORE ACCURATE"]])
    ats = sc.get("row_at", [1.0 + i * 1.4 for i in range(len(rows))])
    for i, (lab, lv, rv) in enumerate(rows):
        p = ease(clamp((t - ats[i]) / 0.5))
        if p <= 0: continue
        y = 400 + i * 150
        for cx, val, good in ((560, lv, False), (1360, rv, True)):
            text_a(img, (cx - 300, y), lab, F("mono", 26), MUTED, p, "lm")
            text_a(img, (cx - 300, y + 50), val, F("disp", 48, "Black"), WHITE, p, "lm", shadow=6)
            ic = (60, 220, 140) if good else T["alert"]; x0 = cx + 250
            d.ellipse([x0 - 34, y - 10, x0 + 34, y + 58], fill=ic + (int(255 * p),))
            if good: d.line([(x0 - 16, y + 24), (x0 - 4, y + 38), (x0 + 18, y + 8)], fill=(255, 255, 255, int(255 * p)), width=8)
            else: d.line([(x0 - 14, y + 10), (x0 + 14, y + 38)], fill=(255, 255, 255, int(255 * p)), width=8); d.line([(x0 + 14, y + 10), (x0 - 14, y + 38)], fill=(255, 255, 255, int(255 * p)), width=8)
    wa = sc.get("win_at", ats[-1] + 1.5); zp = clamp((t - wa) / 0.18)
    if zp > 0:
        st = S.stamp_img(sc.get("stamp", "WINNER"), col=(60, 220, 140), size=96); z = 2.2 - 1.2 * ease(zp)
        st = st.resize((int(st.width * z), int(st.height * z)), Image.LANCZOS).rotate(-8, expand=True, resample=Image.BICUBIC)
        img.alpha_composite(st, (int(1460 - st.width / 2), int(835 - st.height / 2)))
    for i, ln in enumerate(sc.get("lines", [])):
        f = fit_font("disp", 44, ln, 1600, "Bold"); S.rise_line(img, ln, W / 2, 950 + i * 60, f, t - wa - 0.6 - i * 0.6)
    chrome(img, tg, a)

R.SCENE_FN.update({"cartoon": sc_cartoon, "patterns": sc_patterns, "versus": sc_versus})


# ---------------------------------------------------------------- reel 017: the UPI story (16:9)
def _hbar(img, x, y, w, h, frac, col, a, label, val, vf=60):
    rect_a(img, (x, y, x + w, y + h), (30, 28, 22), 0.8 * a, h // 2)
    rect_a(img, (x, y, x + max(h, w * frac), y + h), col, a, h // 2)
    text_a(img, (x, y - 14), label, F("disp", 38, "Black"), WHITE, a, "ls")
    text_a(img, (x + max(h, w * frac) + 18, y + h / 2), val, F("anton", vf), col, a, "lm", shadow=4)

def sc_duel(img, sc, t, D, tg, k):
    """Premise: the daily UPI count vs Visa, then three mystery 'characters' revealed one by one."""
    a = ease(clamp(t / 0.5))
    text_a(img, (120, 250), typed(sc.get("kicker", ""), prog(t, 0.1, 0.6)), F("mono", 32), T["accent"], 1, shadow=4)
    num = sc.get("big", ""); v = float(num.split()[0]); p = ease(clamp((t - 0.3) / 1.6))
    text_a(img, (110, 300), f"{v * p:.0f} {' '.join(num.split()[1:])}", F("anton", 190), WHITE, clamp((t - 0.3) / 0.3), shadow=12)
    text_a(img, (120, 530), sc.get("big_label", ""), F("disp", 44, "Black"), T["accent2"], clamp((t - 0.8) / 0.4))
    rows = sc.get("rows", []); mx = max(r[1] for r in rows)
    for i, (lab, val, s) in enumerate(rows):
        q = ease(clamp((t - 1.2 - i * 0.5) / 1.0))
        _hbar(img, 1040, 340 + i * 190, 640, 64, val / mx * q, T["accent"] if i == 0 else (150, 150, 160), clamp((t - 1.2 - i * 0.5) / 0.3), lab, s)
    ca = sc.get("card_at", [D * 0.55, D * 0.68, D * 0.8])
    for i, lab in enumerate(sc.get("mystery", [])):
        x = 120 + i * 560; y = 700; on = t >= ca[i]; q = ease(clamp((t - 2.0 - i * 0.25) / 0.4))
        if q <= 0: continue
        rect_a(img, (x, y, x + 520, y + 190), (34, 28, 14) if on else (22, 22, 24), 0.92 * q, 22, T["accent"] if on else (80, 80, 84), 3)
        text_a(img, (x + 40, y + 50), f"CHARACTER {i + 1}", F("mono", 26), T["accent2"] if on else MUTED, q)
        if on:
            f = back(clamp((t - ca[i]) / 0.4)); text_a(img, (x + 40, y + 100), lab, fit_font("anton", int(70 * clamp(f, 0.6, 1.1)), lab, 450), WHITE, q)
        else:
            text_a(img, (x + 40, y + 100), "? ? ?", F("anton", 70), MUTED, q)
    chrome(img, tg, a)

_stall = {}
def sc_stall(img, sc, t, D, tg, k):
    """Raju's tea stall (fictional character): props coins | qr | soundbox | photo."""
    a = ease(clamp(t / 0.6)); props = tuple(sc.get("props", []))
    photo = "photo" in props; cx, base, u = (1520, 1010, 3.7) if photo else (1340, 1010, 4.4)
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse([cx - 560, 200, cx + 560, 1120], fill=(255, 170, 60, int(110 * a)))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(140)))
    key = (props, cx, u)
    if key not in _stall: _stall[key] = uu_cartoon.stall_layer(W, H, cx, base, u, props, S.qr_img)
    slide = (1 - a) * 140; bob = 3 * math.sin(tg * 2)
    paste_a(img, _stall[key], (slide, bob), a)
    ct = base - 46 * u + bob; d = ImageDraw.Draw(img)
    text_a(img, (cx + slide, ct + 22 * u), "राजू टी स्टॉल", F("hindi", int(13 * u)), (120, 60, 20), a, "mm")
    st = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
    for j in range(4):                                                        # soft steam from the kettle
        ph = (tg * 0.5 + j / 4) % 1; sx = cx - 54 * u + slide + 6 * u * math.sin(tg * 1.5 + j * 2); sy = ct - 28 * u - ph * 34 * u
        r = 2.5 * u + ph * 5 * u; sd.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(235, 235, 235, int(45 * math.sin(ph * math.pi) * a)))
    img.alpha_composite(st.filter(ImageFilter.GaussianBlur(10)))
    if "soundbox" in props:
        for j in range(3):
            ph = (tg * 0.8 + j / 3) % 1; r = 8 * u + ph * 26 * u; x0 = cx - 32 * u + slide; y0 = ct - 9 * u
            d.ellipse([x0 - r, y0 - r, x0 + r, y0 + r], outline=T["accent2"] + (int(200 * (1 - ph) * a),), width=4)
    if "coins" in props and int(tg * 3) % 2:
        x0 = cx - 27 * u + slide; y0 = ct - 6 * u; d.line([x0 - 8, y0, x0 + 8, y0], fill=(255, 250, 220, 220), width=2); d.line([x0, y0 - 8, x0, y0 + 8], fill=(255, 250, 220, 220), width=2)
    if photo:
        pa = sc.get("photo_at", D * 0.4); q = back(clamp((t - pa) / 0.6))
        if q > 0:
            if "eif" not in _stall: _stall["eif"] = uu_cartoon.eiffel_card(330, 560, S.qr_img)
            pw, ph_ = int(380 * q), int(640 * q)
            if pw > 20:
                ph_im = Image.new("RGBA", (380, 640), (0, 0, 0, 0)); pd = ImageDraw.Draw(ph_im)
                pd.rounded_rectangle([0, 0, 379, 639], 40, fill=(16, 16, 20, 255), outline=T["accent"] + (255,), width=4)
                ph_im.alpha_composite(_stall["eif"], (25, 50))
                pd.text((190, 26), "PARIS · 9:41", font=F("mono", 18), fill=(200, 200, 200, 255), anchor="mm")
                ph_im = ph_im.resize((pw, ph_)).rotate(-6, expand=True, resample=Image.BICUBIC)
                paste_a(img, ph_im, (900 - ph_im.width / 2 + 160, 560 - ph_im.height / 2), clamp((t - pa) / 0.3))
    left_text(img, sc, t, D, y=260, w=620 if photo else 760)
    text_a(img, (W - 24, H - 60), "Illustration · fictional character", F("inter", 18), (190, 180, 160), 0.8 * a, "rm")
    chrome(img, tg, a)

def sc_paynet(img, sc, t, D, tg, k):
    """Banks <-> UPI switch <-> apps on the right; an email-like UPI address typed under the hub; text left."""
    a = ease(clamp(t / 0.5)); la = sc.get("link_at", 1.6); hx, hy = 1420, 560
    banks = sc.get("banks", ["BANK A", "BANK B", "BANK C", "BANK D", "BANK E"])
    apps = sc.get("apps", ["ANY APP", "ANY APP", "ANY APP", "ANY APP", "ANY APP"])
    ys = [270 + i * 145 for i in range(5)]; lp = ease(clamp((t - la) / 0.9)); d = ImageDraw.Draw(img)
    for side, items in ((0, banks), (1, apps)):
        for i, lab in enumerate(items):
            y = ys[i]; x0 = 900 if side == 0 else 1640; ex = x0 + 240 if side == 0 else x0
            if lp > 0:
                d.line([ex, y, ex + (hx - ex) * lp, y + (hy - y) * lp], fill=T["accent2"] + (200,), width=4)
                if lp >= 1:
                    for j in range(2):
                        f = (tg * 0.9 + i * 0.37 + j * 0.5 + side * 0.2) % 1.0; f = f if side == 0 else 1 - f
                        px, py = ex + (hx - ex) * f, y + (hy - y) * f; d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=T["accent"] + (255,))
            q = ease(clamp((t - 0.2 - i * 0.1 - side * 0.3) / 0.4))
            rect_a(img, (x0, y - 44, x0 + 240, y + 44), (26, 26, 24), q * 0.95, 18, T["accent"] if lp > 0 else (90, 90, 84), 3)
            text_a(img, (x0 + 120, y), lab, fit_font("disp", 34, lab, 210, "Black"), WHITE if lp > 0 else MUTED, q, "mm")
    text_a(img, (1020, 200), "BANKS", F("mono", 24), MUTED, a, "mm"); text_a(img, (1760, 200), "APPS", F("mono", 24), MUTED, a, "mm")
    g = ease(clamp((t - la + 0.3) / 0.6))
    if g > 0:
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(glow).ellipse([hx - 160, hy - 160, hx + 160, hy + 160], fill=T["accent"] + (int(120 * g),))
        img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(40)))
        rr = 96 * clamp(back((t - la + 0.3) / 0.6), 0, 1.15); d = ImageDraw.Draw(img)
        d.ellipse([hx - rr, hy - rr, hx + rr, hy + rr], fill=(24, 20, 10, 255), outline=T["accent"] + (255,), width=6)
        text_a(img, (hx, hy - 4), sc.get("hub", "UPI"), F("anton", int(78 * clamp(rr / 96, 0, 1))), T["accent"], g, "mm", shadow=6)
    if sc.get("address"):
        aa = sc.get("addr_at", la + 1.2); q = clamp((t - aa) / 0.3)
        if q > 0:
            s = typed(sc["address"], prog(t, aa, 0.9)); rect_a(img, (hx - 190, 900, hx + 190, 980), (14, 40, 26), q * 0.95, 20, T["accent2"], 3)
            text_a(img, (hx, 940), s, F("mono", 40), WHITE, q, "mm")
    left_text(img, sc, t, D, y=300, w=700)
    chrome(img, tg, a)

def _person(d, x, y, s, col):
    d.ellipse([x - 7 * s, y - 24 * s, x + 7 * s, y - 10 * s], fill=col); d.rounded_rectangle([x - 11 * s, y - 8 * s, x + 11 * s, y + 14 * s], 6 * s, fill=col)

def sc_jio(img, sc, t, D, tg, k):
    """Jio: people pour in (7 per second, 100 M in 170 days), then the price of 1 GB collapses."""
    a = ease(clamp(t / 0.5)); pa = sc.get("price_at", D * 0.6); d = ImageDraw.Draw(img)
    n = int(clamp((t - 0.6) / max(0.1, pa - 0.8)) * 70)
    for i in range(70):
        if i >= n: break
        x = 930 + (i % 14) * 62; y = 330 + (i // 14) * 78; q = clamp((t - 0.6 - i * (pa - 0.8) / 70) / 0.25)
        _person(d, x, y, 1.6, (T["accent2"] if i % 9 else T["accent"]) + (int(255 * q),))
    if t < pa + 0.3:
        c = int(clamp((t - 0.6) / max(0.1, pa - 0.8)) * 100)
        text_a(img, (1360, 820), f"{c} MILLION", F("anton", 96), WHITE, a * clamp((pa + 0.3 - t) / 0.3), "mm", shadow=8)
        text_a(img, (1360, 900), "USERS IN 170 DAYS", F("disp", 36, "Black"), T["accent2"], a * clamp((pa + 0.3 - t) / 0.3), "mm")
    else:
        q = ease(clamp((t - pa) / 0.8)); p0, p1 = sc["p0"], sc["p1"]; base = 900; hmax = 460
        rect_a(img, (900, 220, 1860, 960), (8, 8, 6), 0.85 * clamp((t - pa) / 0.3), 24)
        text_a(img, (1380, 270), "PRICE OF 1 GB MOBILE DATA", F("disp", 40, "Black"), MUTED, clamp((t - pa) / 0.3), "mm")
        rect_a(img, (1040, base - hmax, 1260, base), T["alert"], clamp((t - pa) / 0.3), 16)
        text_a(img, (1150, base - hmax - 50), f"₹{p0}", F("anton", 84), WHITE, clamp((t - pa) / 0.3), "mm")
        text_a(img, (1150, base + 36), "2015–16", F("disp", 34, "Black"), MUTED, clamp((t - pa) / 0.3), "mm")
        h1 = hmax * (p0 + (p1 - p0) * q) / p0; v = p0 + (p1 - p0) * q
        rect_a(img, (1500, base - h1, 1720, base), T["accent2"], clamp((t - pa) / 0.3), 16)
        text_a(img, (1610, base - h1 - 50), f"≈ ₹{v:.0f}", F("anton", 84), T["accent2"], clamp((t - pa) / 0.3), "mm")
        text_a(img, (1610, base + 36), "TODAY", F("disp", 34, "Black"), MUTED, clamp((t - pa) / 0.3), "mm")
    left_text(img, sc, t, D, y=300, w=700)
    chrome(img, tg, a)

def sc_qrtown(img, sc, t, D, tg, k):
    """Note-ban photo first, then a town of stalls where QR stickers pop out from the centre."""
    a = ease(clamp(t / 0.5)); ta = sc.get("town_at", D * 0.42); ca = sc.get("chip_at", D * 0.78)
    if t < ta + 0.6:
        kenburns(img, sc["img"], t, D, k, dark=0.5); gradient(img, "left", 0.9, 0.7)
        fa = clamp((ta + 0.6 - t) / 0.6)
        text_a(img, (120, 300), typed(sc.get("kicker", ""), prog(t, 0.2, 0.8)), F("mono", 32), T["accent"], fa, shadow=4)
        text_a(img, (110, 360), "86%", F("anton", 260), WHITE, fa * clamp((t - 0.6) / 0.3), shadow=12)
        text_a(img, (120, 660), "of India's cash, overnight", F("disp", 54, "Black"), T["accent2"], fa * clamp((t - 1.0) / 0.3), shadow=6)
        credit(img, sc["img"], fa)
    if t >= ta:
        q = clamp((t - ta) / 0.6); img.alpha_composite(Image.new("RGBA", (W, H), T["bg"] + (int(255 * q),)))
        cols, rows, cw = 9, 4, 150
        for r_ in range(rows):
            for c in range(cols):
                dist = math.hypot(c - (cols - 1) / 2, (r_ - (rows - 1) / 2) * 1.2)
                qq = clamp((t - ta - 0.6 - dist * 0.28) / 0.35)
                paste_a(img, S.shop_icon(cw, qq, qq, seed=r_ * cols + c), (W / 2 - cols * 172 / 2 + c * 172, 200 + r_ * 160), q * (0.55 + 0.45 * (qq > 0)))
        if t >= ca:
            cq = clamp((t - ca) / 0.3); p = ease(clamp((t - ca) / 1.0)); v = sc["chip0"] + (sc["chip1"] - sc["chip0"]) * p
            rect_a(img, (W / 2 - 420, 850, W / 2 + 420, 1000), (14, 40, 26), cq * 0.95, 28, T["accent2"], 3)
            text_a(img, (W / 2, 905), f"{sc['chip0']} LAKH → {v:.0f} LAKH", F("anton", 76), WHITE, cq, "mm", shadow=6)
            text_a(img, (W / 2, 968), sc.get("chip", ""), F("inter", 26, "Bold"), T["accent2"], cq, "mm")
        else:
            for i, ln in enumerate(sc.get("lines", [])):
                S.rise_line(img, ln, W / 2, 900 + i * 70, fit_font("disp", 56, ln, W - 200, "Black"), t - ta - 1.5)
    chrome(img, tg, a)

def sc_walletpipe(img, sc, t, D, tg, k):
    """Two lanes: money parked in a wallet box vs money flowing bank-to-bank; then the 96:4 split bar."""
    a = ease(clamp(t / 0.5)); d = ImageDraw.Draw(img); sa = sc.get("split_at", D * 0.62)
    for lane, (y, lab, col) in enumerate(((360, "WALLET", T["alert"]), (640, "UPI", T["accent2"]))):
        q = ease(clamp((t - 0.3 - lane * 0.6) / 0.5))
        if q <= 0: continue
        rect_a(img, (860, y - 60, 1060, y + 60), (26, 26, 24), q, 18, (120, 120, 110), 3); text_a(img, (960, y), "BANK", F("disp", 36, "Black"), WHITE, q, "mm")
        rect_a(img, (1640, y - 60, 1840, y + 60), (26, 26, 24), q, 18, (120, 120, 110), 3); text_a(img, (1740, y), "SHOP", F("disp", 36, "Black"), WHITE, q, "mm")
        text_a(img, (860, y - 92), lab, F("mono", 30), col, q)
        d.line([1060, y, 1640, y], fill=col + (int(160 * q),), width=6)
        if lane == 0:
            rect_a(img, (1260, y - 70, 1440, y + 70), (60, 24, 20), q, 20, col, 4); text_a(img, (1350, y), "WALLET", F("disp", 32, "Black"), WHITE, q, "mm")
            for j in range(3):
                f = (tg * 0.35 + j / 3) % 1; x = 1060 + f * 580
                if 1240 < x < 1460: x = 1350 + 40 * math.sin(tg * 3 + j)           # money waits in the box
                d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=T["accent"] + (int(255 * q),))
        else:
            for j in range(5):
                f = (tg * 0.9 + j / 5) % 1; x = 1060 + f * 580; d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=T["accent"] + (int(255 * q),))
    if t >= sa:
        q = clamp((t - sa) / 0.3); p = ease(clamp((t - sa) / 0.8)); w0, w1 = sc["split"]
        x0, x1, y = 860, 1840, 860; xm = x0 + (x1 - x0) * w0 / 100 * p
        rect_a(img, (x0, y, x1, y + 80), (40, 40, 36), q, 20)
        rect_a(img, (x0, y, xm, y + 80), T["alert"], q, 20); rect_a(img, (x1 - (x1 - x0) * w1 / 100 * p, y, x1, y + 80), T["accent2"], q, 20)
        text_a(img, (x0 + 30, y + 40), f"WALLET {w0 * p:.0f}", F("anton", 52), WHITE, q, "lm")
        text_a(img, (x1 + 10, y + 120), f"UPI {w1}", F("anton", 44), T["accent2"], q, "rm")
    left_text(img, sc, t, D, y=300, w=640)
    chrome(img, tg, a)

def sc_soundbox(img, sc, t, D, tg, k):
    """The talking box: pulses + a Hindi speech bubble; a small chart marks UPI's first billion-payment month."""
    a = ease(clamp(t / 0.5)); d = ImageDraw.Draw(img); cx, cy = 1450, 470
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse([cx - 380, cy - 380, cx + 380, cy + 380], fill=(60, 120, 255, int(70 * a)))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(120)))
    for j in range(3):
        ph = (tg * 0.7 + j / 3) % 1; r = 150 + ph * 260
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=T["accent2"] + (int(170 * (1 - ph) * a),), width=5)
    bx = 150 * a
    d.rounded_rectangle([cx - bx, cy - 170 * a, cx + bx, cy + 170 * a], 60, fill=(28, 38, 70, 255), outline=(120, 150, 230, 255), width=5)
    for r_ in range(5):
        for c in range(5):
            x = cx - 64 + c * 32; y = cy - 120 + r_ * 32; d.ellipse([x - 8, y - 8, x + 8, y + 8], fill=(150, 170, 220, int(255 * a)))
    d.rounded_rectangle([cx - 90, cy + 70, cx + 90, cy + 130], 14, fill=(12, 20, 16, int(255 * a)))
    text_a(img, (cx, cy + 100), "₹10", F("anton", 44), T["accent2"], a, "mm")
    sp = (tg % 3.0) / 3.0
    if sp < 0.6:
        q = clamp(sp / 0.08) * clamp((0.6 - sp) / 0.1); s = sc.get("say", "₹10 प्राप्त हुए")
        f = F("hindi", 54); w = d.textlength(s, font=f)
        rect_a(img, (cx + 150, cy - 290, cx + 150 + w + 60, cy - 190), (250, 250, 245), q, 30)
        d.polygon([(cx + 170, cy - 192), (cx + 230, cy - 192), (cx + 140, cy - 150)], fill=(250, 250, 245, int(255 * q)))
        text_a(img, (cx + 180 + w / 2, cy - 240), s, f, (20, 20, 24), q, "mm")
    ch = sc.get("chart", []); ca = sc.get("chart_at", 0.6)
    if ch:
        x0, yb, bw = 1080, 1000, 160; mx = max(v for _, v in ch)
        for i, (lab, v) in enumerate(ch):
            q = ease(clamp((t - ca - i * 0.4) / 0.7)); h = max(4, 220 * v / mx * q); x = x0 + i * 250
            rect_a(img, (x, yb - h, x + bw, yb), T["accent"] if i == len(ch) - 1 else (120, 116, 100), clamp((t - ca - i * 0.4) / 0.3), 10)
            text_a(img, (x + bw / 2, yb - h - 30), f"{v:g} BN" if v >= 0.1 else "0.0009 BN", F("anton", 34), WHITE, clamp((t - ca - i * 0.4) / 0.3), "mm")
            text_a(img, (x + bw / 2, yb + 26), lab, F("inter", 24, "Bold"), MUTED, clamp((t - ca - i * 0.4) / 0.3), "mm")
    left_text(img, sc, t, D, y=300, w=760)
    chrome(img, tg, a)

def sc_festive(img, sc, t, D, tg, k):
    """Record month over a festive photo: a big centred counter and two cards."""
    a = ease(clamp(t / 0.5))
    kenburns(img, sc["img"], t, D, k, dark=0.55, blur=2); gradient(img, "bottom", 0.9, 0.7)
    text_a(img, (W / 2, 260), typed(sc.get("kicker", ""), prog(t, 0.1, 0.7)), F("mono", 34), T["accent"], 1, "mm", shadow=6)
    p = ease(clamp((t - 0.4) / 2.0)); v = sc["value"] * p
    text_a(img, (W / 2, 450), f"{v:.2f} {sc.get('unit', '')}", F("anton", 200), WHITE, clamp((t - 0.4) / 0.3), "mm", shadow=14)
    text_a(img, (W / 2, 600), sc.get("label", ""), F("disp", 54, "Black"), T["accent2"], clamp((t - 0.9) / 0.4), "mm", shadow=6)
    for i, (big, small) in enumerate(sc.get("items", [])):
        st = sc.get("items_at", [D * 0.35, D * 0.65])[i]; q = clamp((t - st) / 0.35); dy = (1 - back((t - st) / 0.5)) * 60
        x = W / 2 - 700 + i * 720
        rect_a(img, (x, 700 + dy, x + 680, 880 + dy), (10, 10, 8), 0.85 * q, 22, T["accent"], 3)
        text_a(img, (x + 40, 720 + dy), big, F("anton", 76), T["accent"], q, shadow=4)
        text_a(img, (x + 40, 820 + dy), small, F("inter", 34, "SemiBold"), WHITE, q)
    credit(img, sc["img"], a)
    chrome(img, tg, a)

def sc_growth(img, sc, t, D, tg, k):
    """Ten-year counter (1.78 crore -> 24,162 crore a year, x13,000) and UPI vs Visa daily bars."""
    a = ease(clamp(t / 0.5)); ga = sc.get("grow_at", 0.8); va = sc.get("visa_at", D * 0.7)
    text_a(img, (120, 230), typed(sc.get("kicker", ""), prog(t, 0.1, 0.6)), F("mono", 32), T["accent"], 1, shadow=4)
    p = ease(clamp((t - ga) / 2.5)); v0, v1 = sc["v0"], sc["v1"]; v = v0 * (v1 / v0) ** p
    text_a(img, (120, 300), sc.get("y0", ""), F("disp", 40, "Black"), MUTED, a)
    text_a(img, (110, 340), f"{v0}", F("anton", 120), (200, 196, 180), a, shadow=6)
    text_a(img, (120, 520), sc.get("y1", ""), F("disp", 40, "Black"), MUTED, clamp((t - ga) / 0.3))
    text_a(img, (110, 560), f"{v:,.0f}" if v > 100 else f"{v:,.2f}", F("anton", 190), WHITE, clamp((t - ga) / 0.3), shadow=10)
    text_a(img, (120, 790), sc.get("unit", ""), F("disp", 42, "Black"), T["accent2"], clamp((t - ga) / 0.3))
    if p >= 1:
        q = back(clamp((t - ga - 2.5) / 0.5)); f = F("anton", int(90 * clamp(q, 0.1, 1.2)))
        rect_a(img, (820, 600, 1180, 740), T["alert"], clamp((t - ga - 2.5) / 0.2), 26); text_a(img, (1000, 670), "×13,000", f, WHITE, 1, "mm")
    if t >= va:
        q = clamp((t - va) / 0.3); rows = sc.get("duel", []); mx = max(r[1] for r in rows)
        rect_a(img, (1240, 260, 1840, 760), (8, 8, 6), 0.85 * q, 24)
        text_a(img, (1540, 310), sc.get("duel_label", ""), fit_font("disp", 30, sc.get("duel_label", ""), 560, "Black"), MUTED, q, "mm")
        for i, (lab, val) in enumerate(rows):
            qq = ease(clamp((t - va - 0.3 - i * 0.4) / 0.8)); h = 270 * val / mx * qq; x = 1340 + i * 250
            rect_a(img, (x, 700 - h, x + 160, 700), T["accent"] if i == 0 else (150, 150, 160), q, 12)
            text_a(img, (x + 80, 700 - h - 36), f"{val * qq:.0f}", F("anton", 54), WHITE, q, "mm")
            text_a(img, (x + 80, 735), lab, F("disp", 34, "Black"), WHITE, q, "mm")
    chrome(img, tg, a)

R.SCENE_FN.update({"duel": sc_duel, "stall": sc_stall, "paynet": sc_paynet, "jio": sc_jio, "qrtown": sc_qrtown,
                   "walletpipe": sc_walletpipe, "soundbox": sc_soundbox, "festive": sc_festive, "growth": sc_growth})

# ---------------------------------------------------------------- 033: India–Pakistan nuclear list (long)
_site_globe = {}
def sc_sites_l(img, sc, t, D, tg, k):
    lat0, lon0 = 24.0, 74.0
    if k not in _site_globe:
        G = R.Globe(1250); _site_globe[k] = (G, G.render(lat0, lon0, highlight=["IN"], hl_alpha=0.30, dim_others=0.15))
    G, gim = _site_globe[k]
    z = 1.0 + 0.12 * ease_io(t / D)
    cx, cy = G.point(25.0, 64.0, lat0, lon0)[0]
    cw, ch = W / z, H / z
    crop = gim.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize((W, H), Image.BILINEAR)
    img.alpha_composite(crop); img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 80)))
    d = ImageDraw.Draw(img)
    def to_screen(la, lo):
        (px, py), _ = G.point(la, lo, lat0, lon0)
        return (px - (cx - cw / 2)) * z, (py - (cy - ch / 2)) * z
    fields = sc["fields"]; t0 = sc.get("sites_at", 1.2)
    for i, (name, la, lo, cc) in enumerate(fields):
        aa = prog(t, t0 + i * 0.45, 0.4)
        if aa <= 0: continue
        sx, sy = to_screen(la, lo); col = T["accent"] if cc == "IN" else T["accent2"]
        ph = (tg * 0.6 + i * 0.13) % 1; rr = 14 + ph * 34
        d.ellipse([sx - rr, sy - rr, sx + rr, sy + rr], outline=col + (int(200 * (1 - ph) * aa),), width=3)
        d.ellipse([sx - 8, sy - 8, sx + 8, sy + 8], fill=col + (int(255 * aa),))
        text_a(img, (sx + 18, sy + (16 if name == "TROMBAY" else -6)), name, F("mono", 24), WHITE, aa, "lm", shadow=5)
    a = clamp(t / 0.4)
    text_a(img, (90, 150), sc.get("title", ""), F("disp", 56, "Black"), WHITE, a, shadow=8)
    text_a(img, (92, 222), sc.get("sub", ""), F("inter", 26, "Medium"), MUTED, a, shadow=4)
    cats = sc.get("cats", []); c0 = sc.get("cats_at", 0.6)
    for i, c in enumerate(cats):
        aa = prog(t, c0 + i * 0.7, 0.4)
        if aa <= 0: continue
        y = 330 + i * 78
        rect_a(img, (90, y, 640, y + 62), (8, 10, 14), 0.72 * aa, 12)
        rect_a(img, (90, y, 96, y + 62), T["accent"], aa)
        text_a(img, (116, y + 31), c, F("disp", 30, "Bold"), WHITE, aa, "lm")
    if sc.get("total"):
        chip(img, 90, H - 200, sc["total"], T["alert"], prog(t, sc.get("total_at", D - 4), 0.4), 44)
    chrome(img, tg, a)

def sc_gaps_l(img, sc, t, D, tg, k):
    a = clamp(t / 0.4)
    text_a(img, (W / 2, 150), sc.get("kicker", ""), F("mono", 30), T["accent"], a, "mm")
    good, bad = (120, 225, 150), T["alert"]
    for j, (head, col, xs) in enumerate(((sc.get("left", ""), good, 120), (sc.get("right", ""), bad, W / 2 + 30))):
        text_a(img, (xs + 20, 250), head, F("anton", 64), col, a, "lm", shadow=6)
    ats = sc.get("row_at", [1.0, 3.0, 5.0])
    for i, (lab, l, r) in enumerate(sc.get("rows", [])):
        aa = prog(t, ats[i], 0.5); y = 340 + i * 190
        if aa <= 0: continue
        for (txt, col, xs) in ((l, good, 120), (r, bad, W / 2 + 30)):
            rect_a(img, (xs, y, xs + W / 2 - 150, y + 160), (8, 10, 14), 0.72 * aa, 16)
            rect_a(img, (xs, y, xs + 7, y + 160), col, aa)
            text_a(img, (xs + 34, y + 48), lab.upper(), F("mono", 24), MUTED, aa, "lm")
            text_a(img, (xs + 34, y + 105), txt, fit_font("disp", 42, txt, W / 2 - 220, "Bold"), WHITE, aa, "lm")
    if sc.get("lines"):
        la = prog(t, sc.get("line_at", D - 3), 0.5)
        text_a(img, (W / 2, H - 150), sc["lines"][0], F("disp", 52, "Black"), T["accent"], la, "mm", shadow=8)
    chrome(img, tg, a)

R.SCENE_FN.update({"sites": sc_sites_l, "gaps": sc_gaps_l})

if __name__ == "__main__":
    R.main()
