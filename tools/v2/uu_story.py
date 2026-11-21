#!/usr/bin/env python3
"""Vertical STORY Shorts (1080x1920): one big fact told as a documentary, NOT a ranking.

Use this for "how / why / what happened" topics. Use uu_render.py's rank/roll scenes only for real comparisons.
usage: uu_story.py spec.json still t1,t2 | full        (spec "format": "story"; header = the one big fact, shown all along)

Scene types:
  photo   {img*, kicker, big, lines[]}                 full-bleed Ken Burns photo, caption block low-centre, auto credit
  counter {from*, to*, y0, y1, label, chip}           big number ticking down/up with the years, shrinking bar
  bulb    {kicker, big, lines[]}                      a bomb outline morphing into a glowing light bulb
  iceberg {kicker, top_label, top_value, bottom_label, bottom_sub, reveal_at}   announced tip vs hidden mass
  satellite {status: detected|blind, reveal_at, label, night, hud, kicker, big, lines}   spy-satellite sweep over a target
  map     {pin:[lat,lon], pin_label, pin_sub, zoom, zoom_at, labels:[[text,lat,lon]], kicker, big, lines}   India map zoom to a pin
  dossier {file, ref, rows:[[key,val]], stamp, stamp_at, img}   classified file, typed rows, stamp slam
  blast   {date, time, blast_at, hud, kicker, big, lines}       seismograph + night desert shock + dust plume
  booklet {cover, cover_sub, scale, y, stamp, stamp_at, open_at, pages, pages_at, dims_at}   animated passport/booklet
  timeline {kicker, events:[[year, label, note, at?]]}   vertical milestones, last one in red
  borders {lock_at, follow_at, lines}   Europe 1913 free travel -> 1914 routes lock (no internal borders drawn)
  fingerprint {seed, scan_at, match_at, left_label, right_label, stamp}   evidence print scanned, record search flickers, MATCH
  drawers {kicker, whorls:[finger numbers], finger_at, formula_at, drawer_at, lines}   Henry/Haque-Bose primary classification -> 1 of 1,024 drawers
  spread  {origin:[name,lat,lon], year0, routes:[[name,lat,lon,at,from?,year?]]}   arcs across a world map (land only, no borders)
  scanpay {kicker, number, label, lines, pay_at, count_at}   phone scans a QR, ₹10 PAID ripple, big monthly count
  keys    {keys:[[label,sub]...3], key_at[3], kicker, lines}   padlock with 3 keyholes; 3rd key a red "?"
  pricefall {p0, p1, plabel, u0, u1, ulabel, drop_at, use_at, kicker, lines}   price bar collapses, usage bar shoots up
  qrshops {qr_at, count_at, kicker, big, lines}   grid of stalls, QR stickers pop outward, merchant count chip
  network {banks[5], apps[5], hub, link_at, kicker, lines}   banks <-> UPI switch <-> apps with flowing dots
  share   {bars:[[label, pct]], hl, chip, bars_at, hl_at, chip_at, kicker, lines}   market share bars, highlighted row
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

def rise_line(img, ln, cx, cy, f, t, col=(238, 236, 228)):
    """Words rise 26 px and fade in one after another, centred on (cx, cy)."""
    if t <= 0: return
    words = ln.split(" "); d = ImageDraw.Draw(img); sp = d.textlength(" ", font=f)
    ws = [d.textlength(w, font=f) for w in words]; x = cx - (sum(ws) + sp * (len(words) - 1)) / 2
    for j, w in enumerate(words):
        a = ease(clamp((t - j * 0.07) / 0.35))
        if a > 0: text_a(img, (x, cy + 26 * (1 - a)), w, f, col, a, "lm", shadow=8)
        x += ws[j] + sp

def caption(img, sc, t, D, y0=1110):
    text_a(img, (W / 2, y0), typed(sc.get("kicker", ""), prog(t, 0.2, 0.6)), F("mono", 32), T["accent"], 1, "mm", shadow=4)
    if sc.get("big"):
        g = back(clamp((t - 0.5) / 0.5)); s = sc["big"]
        f = fit_font("anton", int(230 * (0.85 + 0.15 * clamp(g, 0, 1.2))), s, W - 120)
        text_a(img, (W / 2, y0 + 170), s, f, WHITE, clamp((t - 0.5) / 0.25), "mm", shadow=12)
    ly = y0 + (330 if sc.get("big") else 110)
    for i, ln in enumerate(sc.get("lines", [])):
        st = 1.0 + i * 0.7
        if R.LOOK == "cinematic":
            rise_line(img, ln, W / 2, ly + i * 70, fit_font("disp", 54, ln, W - 120, "Bold"), t - st)
        else:
            text_a(img, (W / 2, ly + i * 70), typed(ln, prog(t, st, 0.7)), fit_font("disp", 54, ln, W - 120, "Bold"),
                   R.MUTED if R.LIGHT else (238, 236, 228), 1, "mm", shadow=8)

def sc_photo(img, sc, t, D, tg, k):
    kenburns(img, sc["img"], t, D, k)
    img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * sc.get("dark", 0.22)))))
    shade(img)
    caption(img, sc, t + sc.get("cap_lead", 0.0), D, sc.get("cap_y", 1110))
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
    wl = 880                                                         # water line
    a = clamp(t / 0.4); d = ImageDraw.Draw(img)
    text_a(img, (W / 2, 330), typed(sc.get("kicker", ""), prog(t, 0.1, 0.6)), F("mono", 34), T["accent"], 1, "mm", shadow=4)
    # water
    sea = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sea).rectangle([0, wl, W, 1760], fill=(14, 40, 78, int(150 * a)))
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
        bx = (i * 173 + 90) % W; by = 1740 - ((tg * 90 + i * 113) % 840)
        d.ellipse([bx - 5, by - 5, bx + 5, by + 5], outline=T["accent"] + (120,), width=2)
    chrome(img, tg, a)

# ------------------------------------------------------------------ premium scenes (reel 010)
def hud_text(img, xy, s, size=26, col=None, a=1.0, anchor="la"):
    text_a(img, xy, s, F("mono", size), col or T["accent"], a, anchor, shadow=3)

def brackets(d, box, col, L=34, w=4):
    x0, y0, x1, y1 = box
    for (x, y, dx, dy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        d.line([x, y, x + dx * L, y], fill=col, width=w); d.line([x, y, x, y + dy * L], fill=col, width=w)

def draw_sat(d, cx, cy, s, body=(214, 170, 90), panel=(70, 96, 140)):
    d.rectangle([cx - 34 * s, cy - 46 * s, cx + 34 * s, cy + 46 * s], fill=body + (255,), outline=(255, 230, 170, 255), width=max(2, int(3 * s)))
    for sx in (-1, 1):
        x0, x1 = cx + sx * 50 * s, cx + sx * 190 * s
        d.rectangle([min(x0, x1), cy - 30 * s, max(x0, x1), cy + 30 * s], fill=panel + (255,), outline=(170, 200, 240, 255), width=max(2, int(2 * s)))
        for j in range(1, 6):
            xx = x0 + (x1 - x0) * j / 6; d.line([xx, cy - 30 * s, xx, cy + 30 * s], fill=(130, 160, 210, 255), width=1)
        d.line([cx + sx * 34 * s, cy, x0, cy], fill=(200, 200, 200, 255), width=max(2, int(3 * s)))
    d.ellipse([cx - 22 * s, cy + 40 * s, cx + 22 * s, cy + 66 * s], outline=(240, 240, 240, 255), width=max(2, int(3 * s)))

def desert_ground(img, y_top, tg, a=1.0, night=0.0):
    """Layered dune silhouettes from y_top down, with a faint grid (satellite view)."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    base = T["land"]
    for j in range(4):
        yb = y_top + j * 70; amp = 26 - j * 4
        pts = [(x, yb + amp * math.sin(x / (170 + j * 40) + j * 1.7 + tg * 0.05)) for x in range(0, W + 20, 20)]
        c = tuple(int(v * (0.75 + 0.18 * j) * (1 - 0.55 * night)) for v in base)
        d.polygon(pts + [(W, H), (0, H)], fill=c + (int(255 * a),))
    for x in range(0, W, 90): d.line([x, y_top + 40, x, H], fill=T["land_edge"] + (int(28 * a),), width=1)
    for y in range(int(y_top) + 40, H, 90): d.line([0, y, W, y], fill=T["land_edge"] + (int(28 * a),), width=1)
    img.alpha_composite(lay)

def sc_satellite(img, sc, t, D, tg, k):
    """A spy satellite crosses the sky and sweeps its scan beam over the target. status: detected | blind."""
    a = clamp(t / 0.4); night = sc.get("night", 0.0)
    if night:
        img.alpha_composite(Image.new("RGBA", (W, H), (4, 6, 20, int(150 * night))))
        dd = ImageDraw.Draw(img); r = np.random.default_rng(7)
        for _ in range(140):
            x, y = r.uniform(0, W), r.uniform(150, 900); tw = 0.5 + 0.5 * math.sin(tg * 3 + x)
            dd.ellipse([x - 1.5, y - 1.5, x + 1.5, y + 1.5], fill=(255, 255, 240, int(200 * tw)))
        dd.ellipse([840, 230, 940, 330], fill=(250, 244, 220, 255)); dd.ellipse([870, 220, 960, 320], fill=(9, 10, 26, 255))
    desert_ground(img, 900, tg, a, night)
    tx, ty = W / 2, 980                                              # target on the ground
    sx = -260 + (W + 520) * clamp(t / max(D, 0.1))                   # satellite crosses the frame
    sy = 420 + 40 * math.sin(t * 0.8)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    sweep = 0.5 + 0.5 * math.sin(tg * 2.2)
    beam_a = int(90 * a * (0.6 + 0.4 * sweep))
    bw = 150 + 60 * sweep
    d.polygon([(sx, sy + 40), (tx - bw, ty + 30), (tx + bw, ty + 30)], fill=T["accent"] + (beam_a // 2,))
    d.line([sx, sy + 40, tx - bw, ty + 30], fill=T["accent"] + (beam_a,), width=2); d.line([sx, sy + 40, tx + bw, ty + 30], fill=T["accent"] + (beam_a,), width=2)
    sl = ty - 90 + (tg * 160) % 180                                  # scan line over the target box
    d.line([tx - 190, sl, tx + 190, sl], fill=T["accent"] + (160,), width=3)
    lay = lay.filter(ImageFilter.GaussianBlur(1.2)); img.alpha_composite(lay)
    d = ImageDraw.Draw(img)
    draw_sat(d, sx, sy, 1.15)
    rev = prog(t, sc.get("reveal_at", 2.0), 0.4)
    det = sc.get("status") == "detected"
    col = (T["alert"] if det else (90, 230, 140)) if rev > 0 else T["accent"]
    brackets(d, (tx - 200, ty - 100, tx + 200, ty + 100), col + (255,), 40, 5)
    if det and rev > 0:
        for i in range(5):
            bx = tx - 120 + (i * 61) % 240; by = ty - 50 + (i * 37) % 100
            d.rectangle([bx - 14, by - 10, bx + 14, by + 10], outline=T["alert"] + (int(255 * rev),), width=3)
    hud_text(img, (60, 340), sc.get("hud", "SAT-PASS  //  TARGET: POKHRAN  27.09°N 71.75°E"), 24, a=a)
    hud_text(img, (60, 376), f"T+{tg:06.2f}s   ORBIT 400 KM   RES 0.3 M", 22, MUTED, a)
    if rev > 0:
        lab = sc.get("label", "ACTIVITY DETECTED" if det else "NO ACTIVITY FOUND")
        f = F("anton", 64); w = ImageDraw.Draw(img).textlength(lab, font=f)
        blink = 1.0 if (not det or int(tg * 3) % 2 == 0) else 0.65
        rect_a(img, (tx - w / 2 - 30, ty - 190, tx + w / 2 + 30, ty - 110), col, 0.92 * rev * blink, 10)
        text_a(img, (tx, ty - 150), lab, f, (12, 12, 12), rev, "mm")
    caption(img, sc, t, D)
    chrome(img, tg, a)

def _proj(lat, lon, c_lat, c_lon, s, cx, cy):
    return cx + (lon - c_lon) * s * math.cos(math.radians(c_lat)), cy - (lat - c_lat) * s

def sc_map(img, sc, t, D, tg, k):
    """India outline draws itself, then the camera zooms into the pin (Pokhran)."""
    a = clamp(t / 0.4)
    lat1, lon1 = sc.get("pin", [27.09, 71.75])
    z = ease_io(prog(t, sc.get("zoom_at", 1.6), 1.8))
    c_lat = 22.5 + (lat1 - 22.5) * z; c_lon = 80.0 + (lon1 - 80.0) * z
    sc0, sc1 = 30.0, 30.0 * sc.get("zoom", 3.2); s_ = sc0 * (sc1 / sc0) ** z
    cx, cy = W / 2, 640
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    draw_p = clamp(t / 1.4)
    for iso, rings in R.COUNTRIES:
        for ring in rings:
            lons, lats = np.degrees(ring[:, 0]), np.degrees(ring[:, 1])
            if lons.max() < 55 or lons.min() > 100 or lats.max() < 0 or lats.min() > 40: continue
            pts = [_proj(la, lo, c_lat, c_lon, s_, cx, cy) for lo, la in zip(lons, lats)]
            if iso == "IN":
                d.polygon(pts, fill=(96, 68, 38, int(230 * a)))
                n = max(2, int(len(pts) * draw_p)); d.line(pts[:n], fill=T["accent"] + (255,), width=4)
            else:
                d.polygon(pts, fill=(48, 44, 60, int(210 * a)), outline=T["land_edge"] + (int(120 * a),))
    img.alpha_composite(lay)
    px, py = _proj(lat1, lon1, c_lat, c_lon, s_, cx, cy)
    pa = prog(t, sc.get("zoom_at", 1.6) + 1.2, 0.4)
    if pa > 0:
        d = ImageDraw.Draw(img)
        for j in range(3):
            rr = 20 + ((tg * 70 + j * 40) % 120)
            d.ellipse([px - rr, py - rr, px + rr, py + rr], outline=T["alert"] + (int(220 * pa * (1 - rr / 140)),), width=4)
        d.ellipse([px - 14, py - 14, px + 14, py + 14], fill=T["alert"] + (255,), outline=(255, 255, 255, 255), width=3)
        text_a(img, (px + 40, py - 30), sc.get("pin_label", "POKHRAN"), F("anton", 76), WHITE, pa, "lm", shadow=10)
        text_a(img, (px + 42, py + 30), sc.get("pin_sub", "Jaisalmer · Rajasthan"), F("inter", 32, "SemiBold"), T["accent2"], pa, "lm", shadow=6)
    for lab, la, lo in sc.get("labels", []):
        lx, ly = _proj(la, lo, c_lat, c_lon, s_, cx, cy)
        if 60 < lx < W - 60 and 300 < ly < 1000: text_a(img, (lx, ly), lab, F("mono", 24), MUTED, a * (1 - z * 0.5) * (1 - pa), "mm")
    caption(img, sc, t, D)
    chrome(img, tg, a)

_paper = None
def paper(w, h):
    global _paper
    if _paper is None or _paper.size != (w, h):
        r = np.random.default_rng(3); n = r.normal(0, 9, (h, w))
        base = np.array([232, 220, 194], np.float32)[None, None, :] + n[..., None]
        yy, xx = np.mgrid[0:h, 0:w]; edge = np.clip(np.minimum.reduce([xx, yy, w - xx, h - yy]) / 60, 0, 1)
        base *= (0.82 + 0.18 * edge)[..., None]
        _paper = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    return _paper.copy()

def draw_dossier(img, sc, t, x0=None, y0=300):
    """The file card (880x700) with typed rows and a stamp; x0=None centres it. Returns the fade-in alpha."""
    a = ease(clamp(t / 0.5)); pw, ph = 880, 700
    card = paper(pw, ph); d = ImageDraw.Draw(card)
    d.rectangle([0, 0, pw, 70], fill=(196, 170, 120, 255)); d.text((30, 18), sc.get("file", "FILE"), font=F("mono", 30), fill=(40, 30, 20))
    d.text((pw - 30, 18), sc.get("ref", "REF/PKN"), font=F("mono", 24), fill=(60, 45, 30), anchor="ra")
    y = 110
    for i, (key, val) in enumerate(sc.get("rows", [])):
        p = prog(t, 0.5 + i * 0.55, 0.5)
        d.text((40, y), key, font=F("mono", 26), fill=(110, 90, 70))
        d.text((300, y), typed(val, p), font=fit_font("mono", 34, val, pw - 340), fill=(25, 22, 18)); y += 72
        d.line([40, y - 14, pw - 40, y - 14], fill=(190, 175, 150), width=1)
    if sc.get("img"):
        ph_im = load(sc["img"]).copy(); ph_im.thumbnail((260, 200)); fr = Image.new("RGBA", (ph_im.width + 20, ph_im.height + 20), (250, 248, 240, 255))
        fr.paste(ph_im.convert("RGBA"), (10, 10)); fr = fr.rotate(4, expand=True, resample=Image.BICUBIC)
        card.alpha_composite(fr, (pw - fr.width - 30, ph - fr.height - 30))
    st_at = sc.get("stamp_at", 0.5 + len(sc.get("rows", [])) * 0.55 + 0.4)
    sp = clamp((t - st_at) / 0.18)
    if sp > 0:
        lab = sc.get("stamp", "TOP SECRET"); f = F("anton", 92); tw = d.textlength(lab, font=f)
        st = Image.new("RGBA", (int(tw) + 70, 150), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
        sd.rounded_rectangle([6, 6, st.width - 6, 144], 12, outline=(200, 30, 30, 235), width=8)
        sd.text((st.width / 2, 76), lab, font=f, fill=(200, 30, 30, 235), anchor="mm")
        sc_ = 2.2 - 1.2 * ease(sp); st = st.resize((int(st.width * sc_), int(st.height * sc_)), Image.LANCZOS).rotate(-12, expand=True, resample=Image.BICUBIC)
        card.alpha_composite(st, (int(pw / 2 - st.width / 2 - 40), int(ph * 0.62 - st.height / 2)))
    shake = 10 * max(0, 1 - (t - st_at) / 0.25) if t > st_at else 0
    card = card.rotate(-2.5 + 2.5 * (1 - a), expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", card.size, (0, 0, 0, 0)); sh.putalpha(card.getchannel("A").point(lambda v: v // 2))
    xc = (W / 2 - card.width / 2) if x0 is None else x0
    x = xc + (1 - a) * 300 + shake * math.sin(t * 90); y = y0 + shake * math.cos(t * 80)
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)), (int(x + 16), int(y + 24)))
    paste_a(img, card, (x, y), a)
    return a

def sc_dossier(img, sc, t, D, tg, k):
    """A classified file slides in, lines are typed, then a red stamp slams down."""
    a = draw_dossier(img, sc, t)
    caption(img, sc, t, D, 1180)
    if sc.get("img"): credit(img, sc["img"], a)
    chrome(img, tg, a)

def sc_blast(img, sc, t, D, tg, k):
    """Night desert, a seismograph trace; at blast_at the ground jumps: flash, shock ring, dust plume."""
    a = clamp(t / 0.4); bt = sc.get("blast_at", 1.6); after = t - bt
    shake = 14 * max(0, 1 - after / 0.6) if after > 0 else 0
    img.alpha_composite(Image.new("RGBA", (W, H), (4, 6, 20, 140)))
    dd = ImageDraw.Draw(img); r = np.random.default_rng(11)
    for _ in range(120):
        x, y = r.uniform(0, W), r.uniform(560, 860); dd.ellipse([x - 1.4, y - 1.4, x + 1.4, y + 1.4], fill=(255, 250, 230, 170))
    hy = 980 + shake * math.sin(t * 70)
    if after > 0:   # glow, rising dust column with a spreading cap, ground shock ring
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        pr = ease(clamp(after / 2.2)); fade = 1 - 0.5 * clamp((after - 2.2) / 3)
        gl = 1 - clamp(after / 1.5)
        d.ellipse([W / 2 - 420, hy - 160, W / 2 + 420, hy + 120], fill=(255, 150, 60, int(170 * gl)))
        top = hy - 40 - 360 * pr
        for j in range(14):
            yy = hy - 20 - (hy - 20 - top) * j / 13; rr = 46 + 18 * math.sin(j * 1.3 + tg * 2) + 10 * j * pr
            d.ellipse([W / 2 - rr, yy - rr * 0.8, W / 2 + rr, yy + rr * 0.8], fill=(214, 160, 104, int(150 * fade)))
        cw = 90 + 230 * pr
        for j in range(5):
            ox = (j - 2) * cw * 0.42; d.ellipse([W / 2 + ox - cw * 0.55, top - cw * 0.35, W / 2 + ox + cw * 0.55, top + cw * 0.3], fill=(226, 176, 120, int(140 * fade)))
        rw = 80 + 900 * clamp(after / 1.2)
        d.ellipse([W / 2 - rw, hy - rw * 0.08, W / 2 + rw, hy + rw * 0.08], outline=T["accent"] + (int(230 * (1 - clamp(after / 1.2))),), width=8)
        img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(10)))
    desert_ground(img, hy, tg, a, 0.7)
    # seismograph panel
    px0, py0, px1, py1 = 70, 300, W - 70, 520
    rect_a(img, (px0, py0, px1, py1), (8, 10, 14), 0.85 * a, 16, T["land_edge"], 2)
    hud_text(img, (px0 + 20, py0 + 14), sc.get("hud", "SEISMIC STATION // RAJASTHAN"), 22, a=a)
    d = ImageDraw.Draw(img); pts = []
    for i in range(160):
        x = px0 + 20 + i * (px1 - px0 - 40) / 159; tt = t - (159 - i) * 0.02
        amp = 6 + (180 * math.exp(-max(0, tt - bt) * 2.2) if tt > bt else 0)
        pts.append((x, (py0 + py1) / 2 + 20 + amp * math.sin(i * 1.7 + tg * 9) * (0.5 + 0.5 * math.sin(i * 0.37))))
    d.line(pts, fill=(T["alert"] if after > 0 else T["accent"]) + (255,), width=3)
    if 0 < after < 0.25:
        img.alpha_composite(Image.new("RGBA", (W, H), (255, 236, 200, int(230 * (1 - after / 0.25)))))
    text_a(img, (W / 2, 640), sc.get("date", ""), F("anton", 120), WHITE, prog(t, 0.2, 0.4), "mm", shadow=12)
    text_a(img, (W / 2, 750), sc.get("time", ""), F("mono", 44), T["accent"], prog(t, 0.5, 0.4), "mm", shadow=6)
    caption(img, sc, max(0, t - bt + 0.3), D, 1110)
    chrome(img, tg, a)

# ------------------------------------------------------------------ passport scenes (reel 011)
def stamp_img(lab, col=(200, 30, 30), size=92):
    f = F("anton", size); tw = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textlength(lab, font=f)
    st = Image.new("RGBA", (int(tw) + 70, int(size * 1.6)), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
    sd.rounded_rectangle([6, 6, st.width - 6, st.height - 6], 12, outline=col + (235,), width=8)
    sd.text((st.width / 2, st.height / 2 + 4), lab, font=f, fill=col + (235,), anchor="mm")
    a = np.array(st); m = np.random.default_rng(5).random(a.shape[:2]) < 0.14; a[m, 3] = a[m, 3] // 3
    return Image.fromarray(a)

BW, BH = 380, 560                                                   # booklet page size (15.5 x 10.5 ratio)
GOLD = (214, 180, 100)
_bk = {}
def _cover(title, sub):
    k = ("cover", title, sub)
    if k in _bk: return _bk[k]
    r = np.random.default_rng(9); n = r.normal(0, 5, (BH, BW))
    xx = np.linspace(0, 1, BW)[None, :]
    base = np.array([26, 40, 78], np.float32)[None, None, :] * (0.8 + 0.3 * np.sin(xx * math.pi))[..., None] + n[..., None]
    im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    m = Image.new("L", (BW, BH), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, BW - 1, BH - 1], 14, fill=255); im.putalpha(m)
    d = ImageDraw.Draw(im); g = GOLD + (255,)
    d.rounded_rectangle([16, 16, BW - 16, BH - 16], 10, outline=g, width=3)
    d.text((BW / 2, 104), title, font=fit_font("disp", 54, title, BW - 70, "Black"), fill=g, anchor="mm")
    cx, cy = BW / 2, 290
    d.ellipse([cx - 80, cy - 80, cx + 80, cy + 80], outline=g, width=5)
    pts = [(cx + (58 if i % 2 == 0 else 24) * math.sin(i * math.pi / 5), cy - (58 if i % 2 == 0 else 24) * math.cos(i * math.pi / 5)) for i in range(10)]
    d.polygon(pts, fill=g)
    for side in (-1, 1):
        for j in range(8):
            an = math.radians(200 + j * 17); rx, ry = cx + side * 108 * math.cos(an) * -1, cy + 108 * math.sin(an) * -1
            d.ellipse([rx - 11, ry - 6, rx + 11, ry + 6], fill=g)
    d.text((BW / 2, 450), sub, font=fit_font("inter", 26, sub, BW - 70, "SemiBold"), fill=g, anchor="mm")
    _bk[k] = im; return im

def _page(kind):
    if kind in _bk: return _bk[kind]
    r = np.random.default_rng(4 if kind == "right" else 6); n = r.normal(0, 7, (BH, BW))
    base = np.array([236, 226, 200] if kind == "right" else [214, 200, 168], np.float32)[None, None, :] + n[..., None]
    im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB").convert("RGBA"); d = ImageDraw.Draw(im)
    if kind == "right":
        d.text((24, 26), "DESCRIPTION · SIGNALEMENT", font=F("mono", 20), fill=(90, 70, 50))
        d.rectangle([BW - 140, 70, BW - 24, 220], outline=(120, 100, 80), width=2)
        d.ellipse([BW - 108, 96, BW - 56, 152], fill=(170, 155, 130)); d.chord([BW - 126, 150, BW - 38, 240], 180, 360, fill=(170, 155, 130))
        d.rectangle([BW - 141, 221, BW - 23, 240], fill=(236, 226, 200))
        for i, lab in enumerate(["Profession", "Place of birth", "Residence", "Height", "Forehead", "Eyes", "Nose", "Mouth", "Face", "Complexion"]):
            y = 82 + i * 46 if i < 3 else 270 + (i - 3) * 40
            d.text((24, y), lab, font=F("mono", 19), fill=(110, 90, 70))
            d.line([24, y + 30, (BW - 160) if i < 3 else BW - 24, y + 30], fill=(180, 165, 140), width=1)
    else:
        d.rectangle([20, 20, BW - 20, BH - 20], outline=(150, 130, 100), width=2)
    _bk[kind] = im; return im

def _squash(im, w):
    w = max(1, int(w)); return im.resize((w, im.height), Image.BILINEAR)

def draw_booklet(img, sc, t, cx, ytop):
    """Draw the booklet centred on x=cx (closed) with its top at ytop. Shared by the vertical and 16:9 renderers."""
    a = ease(clamp(t / 0.5)); y0 = ytop + (1 - a) * 120
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(lay).ellipse([cx - 520, y0 - 120, cx + 520, y0 + BH + 140], fill=T["glow"] + (150,))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(90)))
    op = ease_io(clamp((t - sc["open_at"]) / 1.1)) if sc.get("open_at") is not None else 0.0
    sx = cx - BW / 2 * (1 - op)                                      # spine x
    book = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    th = math.pi * op
    if op > 0:
        rp = _page("right").copy()
        book.alpha_composite(rp, (int(sx), int(y0)))
        for j in range(5): ImageDraw.Draw(book).line([sx + BW + j, y0 + 4 + j, sx + BW + j, y0 + BH - 4 + j], fill=(200, 190, 165, 255))
    if th < math.pi / 2:
        cv = _cover(sc.get("cover", "PASSPORT"), sc.get("cover_sub", ""))
        w = BW * math.cos(th); c2 = _squash(cv, w)
        if op > 0: c2 = Image.alpha_composite(c2, Image.new("RGBA", c2.size, (0, 0, 0, int(140 * op))))
        book.alpha_composite(c2, (int(sx), int(y0)))
    else:
        lp = _page("left").copy(); d = ImageDraw.Draw(lp)
        if sc.get("pages"):
            pp = clamp((t - sc.get("pages_at", 3)) / 2.2); n = int(round(sc["pages"] * pp))
            d.text((BW / 2, BH / 2 - 40), f"{n}", font=F("anton", 210), fill=(60, 40, 25), anchor="mm")
            d.text((BW / 2, BH / 2 + 90), "PAGES", font=F("disp", 48, "Black"), fill=(110, 80, 50), anchor="mm")
        w = BW * -math.cos(th); book.alpha_composite(_squash(lp, w), (int(sx - w), int(y0)))
        ImageDraw.Draw(book).line([sx, y0, sx, y0 + BH], fill=(120, 100, 70, 255), width=3)
    if sc.get("pages") and op >= 1:                                  # flipping sheets
        ft = t - sc.get("pages_at", 3)
        if 0 < ft < 2.2:
            ph = (ft % 0.28) / 0.28; w = BW * math.cos(math.pi * ph)
            sh = _page("right").copy(); sh = Image.alpha_composite(sh, Image.new("RGBA", sh.size, (0, 0, 0, int(60 * abs(math.sin(math.pi * ph))))))
            if w > 0: book.alpha_composite(_squash(sh, w), (int(sx), int(y0)))
            else: book.alpha_composite(_squash(_page("left"), -w), (int(sx + w), int(y0)))
    z = sc.get("scale", 1.0)
    if z != 1.0:                                                     # scale the whole booklet about its centre
        cxb, cyb = cx, y0 + BH / 2; big = book.resize((int(W * z), int(H * z)), Image.BICUBIC)
        book = Image.new("RGBA", (W, H), (0, 0, 0, 0)); book.alpha_composite(big, (int(cxb - cxb * z), int(cyb - cyb * z)))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); shadow.putalpha(book.getchannel("A").point(lambda v: int(v * 0.6)))
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(22)), (14, 26))
    if sc.get("stamp"):
        sp = clamp((t - sc.get("stamp_at", 2.0)) / 0.18)
        if sp > 0:
            st = stamp_img(sc["stamp"], size=78); z = 2.4 - 1.4 * ease(sp)
            st = st.resize((int(st.width * z), int(st.height * z)), Image.LANCZOS).rotate(14, expand=True, resample=Image.BICUBIC)
            cx = sx + (BW / 2 if op < 0.5 else BW / 2); book.alpha_composite(st, (int(cx - st.width / 2), int(y0 + BH * 0.62 - st.height / 2)))
    shake = 0
    if sc.get("stamp") and t > sc.get("stamp_at", 2.0): shake = 9 * max(0, 1 - (t - sc.get("stamp_at", 2.0)) / 0.25)
    paste_a(img, book, (shake * math.sin(t * 90), shake * math.cos(t * 70)), a)
    if sc.get("dims_at") is not None:
        da = ease(clamp((t - sc["dims_at"]) / 0.6)); rx0, rx1 = sx, sx + BW
        if da > 0:
            d = ImageDraw.Draw(img); c = T["accent"] + (int(255 * da),)
            vx = rx1 + 34; d.line([vx, y0, vx, y0 + BH * da], fill=c, width=4)
            for yy, dr in ((y0, 1), (y0 + BH * da, -1)): d.polygon([(vx, yy), (vx - 12, yy + dr * 20), (vx + 12, yy + dr * 20)], fill=c)
            hy = y0 + BH + 34; d.line([rx0, hy, rx0 + BW * da, hy], fill=c, width=4)
            for xx, dr in ((rx0, 1), (rx0 + BW * da, -1)): d.polygon([(xx, hy), (xx + dr * 20, hy - 12), (xx + dr * 20, hy + 12)], fill=c)
            lab = Image.new("RGBA", (260, 64), (0, 0, 0, 0)); ImageDraw.Draw(lab).text((130, 32), "15.5 cm", font=F("anton", 52), fill=WHITE + (255,), anchor="mm")
            paste_a(img, lab.rotate(90, expand=True), (vx + 6, y0 + BH / 2 - 130), da)
            text_a(img, (rx0 + BW / 2, hy + 44), "10.5 cm", F("anton", 52), WHITE, da, "mm", shadow=6)
    return a

def sc_booklet(img, sc, t, D, tg, k):
    """A 1920s-style passport booklet: slides in, can take a stamp, open, flip its pages and show its size."""
    a = draw_booklet(img, sc, t, W / 2, sc.get("y", 330))
    caption(img, sc, t, D, 1110 if sc.get("dims_at") is None else 1130)
    chrome(img, tg, a)

def sc_timeline(img, sc, t, D, tg, k):
    """Vertical timeline: a gold line grows and each milestone slides in (the last one in alert red)."""
    ev = sc["events"]; n = len(ev); a = clamp(t / 0.4)
    text_a(img, (W / 2, 330), typed(sc.get("kicker", ""), prog(t, 0.1, 0.6)), F("mono", 34), T["accent"], 1, "mm", shadow=4)
    x0 = 160; ys = [470 + i * 300 for i in range(n)]
    ats = [e[3] if len(e) > 3 else 0.6 + i * (D - 1.4) / n for i, e in enumerate(ev)]
    rect_a(img, (x0 - 3, ys[0], x0 + 3, ys[-1]), MUTED, 0.25 * a)
    cur = ys[0]
    for i in range(n):
        p = prog(t, ats[i], 0.6)
        if p > 0: cur = ys[i - 1] + (ys[i] - ys[i - 1]) * p if i > 0 else ys[0]
    rect_a(img, (x0 - 4, ys[0], x0 + 4, cur), T["accent"], a)
    d = ImageDraw.Draw(img)
    for i, e in enumerate(ev):
        p = prog(t, ats[i], 0.6)
        if p <= 0: continue
        last = i == n - 1; col = T["alert"] if (last or "not" in e[2].lower()) else T["accent"]
        y = ys[i]; dx = (1 - p) * 80
        if i == max(j for j in range(n) if t >= ats[j]):
            for j in range(2):
                rr = 18 + ((tg * 50 + j * 30) % 60)
                d.ellipse([x0 - rr, y - rr, x0 + rr, y + rr], outline=col + (int(200 * (1 - rr / 80)),), width=3)
        d.ellipse([x0 - 18, y - 18, x0 + 18, y + 18], fill=col + (255,), outline=(255, 255, 255, 255), width=3)
        text_a(img, (x0 + 60 + dx, y - 24), e[0], F("anton", 112), col, p, "lm", shadow=8)
        text_a(img, (x0 + 330 + dx, y - 44), e[1], fit_font("disp", 52, e[1], W - x0 - 400, "Black"), WHITE, p, "lm", shadow=6)
        text_a(img, (x0 + 330 + dx, y + 14), typed(e[2], prog(t, ats[i] + 0.3, 0.6)), fit_font("inter", 38, e[2], W - x0 - 400, "SemiBold"),
               T["accent2"] if not last else WHITE, p, "lm", shadow=6)
    chrome(img, tg, a)

CITIES = {"LONDON": (51.5, -0.13, 0), "PARIS": (48.86, 2.35, 0), "BERLIN": (52.52, 13.4, 0), "ROME": (41.9, 12.5, 0),
          "MADRID": (40.42, -3.7, 1), "COPENHAGEN": (55.68, 12.57, 1), "BERN": (46.95, 7.45, 1)}
ROUTES = [("LONDON", "PARIS"), ("PARIS", "BERLIN"), ("PARIS", "MADRID"), ("PARIS", "BERN"), ("BERN", "ROME"), ("BERLIN", "COPENHAGEN"),
          ("BERLIN", "ROME"), ("LONDON", "COPENHAGEN"), ("MADRID", "ROME"), ("BERLIN", "BERN")]
EU = dict(c_lat=47.5, c_lon=6.0, s=36.0, cx=W / 2, cy=660)
_eu = {}
def _europe(eu=None):
    eu = eu or EU; key = tuple(sorted(eu.items()))
    if key not in _eu:
        EU_ = eu
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        for iso, rings in R.COUNTRIES:
            for ring in rings:
                lons, lats = np.degrees(ring[:, 0]), np.degrees(ring[:, 1])
                if lons.max() < -25 or lons.min() > 45 or lats.max() < 30 or lats.min() > 72: continue
                pts = [_proj(la, lo, EU_["c_lat"], EU_["c_lon"], EU_["s"], EU_["cx"], EU_["cy"]) for lo, la in zip(lons, lats)]
                d.polygon(pts, fill=(78, 62, 42, 255), outline=(78, 62, 42, 255))
        glow = Image.new("RGBA", (W, H), T["accent"] + (0,)); glow.putalpha(lay.getchannel("A").filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * 0.5)))
        out = Image.new("RGBA", (W, H), (0, 0, 0, 0)); out.alpha_composite(glow); out.alpha_composite(lay)
        _eu[key] = out
    return _eu[key]

def _cpos(name, eu=None):
    eu = eu or EU; la, lo, _ = CITIES[name]; return _proj(la, lo, eu["c_lat"], eu["c_lon"], eu["s"], eu["cx"], eu["cy"])

def _padlock(d, x, y, col, s=1.0):
    d.arc([x - 13 * s, y - 30 * s, x + 13 * s, y - 2 * s], 180, 360, fill=col, width=int(5 * s))
    d.rounded_rectangle([x - 18 * s, y - 14 * s, x + 18 * s, y + 16 * s], int(5 * s), fill=col)

def draw_borders(img, sc, t, tg, a, eu=None):
    """Map, routes, travellers and capitals. Returns True while still 1913 (before lock_at)."""
    eu = eu or EU; la_, fo_ = sc.get("lock_at", 1.6), sc.get("follow_at", 4.5)
    paste_a(img, _europe(eu), (0, 0), a)
    locked = {c for c, v in CITIES.items() if (t >= la_ and v[2] == 0) or (t >= fo_ and v[2] == 1)}
    d = ImageDraw.Draw(img)
    for r_i, (c1, c2) in enumerate(ROUTES):
        (x1, y1), (x2, y2) = _cpos(c1, eu), _cpos(c2, eu)
        mx, my = (x1 + x2) / 2 - (y2 - y1) * 0.18, (y1 + y2) / 2 + (x2 - x1) * 0.18
        pts = [((1 - u) ** 2 * x1 + 2 * (1 - u) * u * mx + u * u * x2, (1 - u) ** 2 * y1 + 2 * (1 - u) * u * my + u * u * y2) for u in np.linspace(0, 1, 40)]
        closed = c1 in locked or c2 in locked
        col = (T["alert"] if closed else T["accent2"]) + (int((200 if closed else 150) * a),)
        for j in range(0, 39, 2): d.line([pts[j], pts[j + 1]], fill=col, width=4)
        if not closed:
            for q in range(3):
                u = ((tg * 0.35 + q / 3 + r_i * 0.13) % 1.0); x, y = pts[int(u * 39)]
                d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(255, 240, 200, int(255 * a)))
        else:
            x, y = pts[20]; d.ellipse([x - 17, y - 17, x + 17, y + 17], fill=T["alert"] + (255,)); d.rectangle([x - 10, y - 3, x + 10, y + 3], fill=(255, 255, 255, 255))
    for c, (la, lo, neu) in CITIES.items():
        x, y = _cpos(c, eu); lk = c in locked
        t0 = la_ if neu == 0 else fo_
        if lk and t - t0 < 1.0:
            rr = 20 + 120 * (t - t0); d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=T["alert"] + (int(230 * (1 - (t - t0))),), width=5)
        d.ellipse([x - 11, y - 11, x + 11, y + 11], fill=(T["alert"] if lk else WHITE) + (255,), outline=(20, 14, 8, 255), width=3)
        lx = x + (16 if c not in ("MADRID", "LONDON") else -16); anc = "lm" if c not in ("MADRID", "LONDON") else "rm"
        text_a(img, (lx, y - 26), c, F("mono", 24), T["alert"] if lk else WHITE, a, anc, shadow=6)
        if lk: _padlock(ImageDraw.Draw(img), x + (30 if anc == "lm" else -30), y + 20, T["alert"] + (255,), 0.8)
    return t < la_

def sc_borders(img, sc, t, D, tg, k):
    """Europe 1913: travellers flow freely between capitals. At lock_at the warring states lock; neutrals follow at follow_at."""
    a = clamp(t / 0.5); la_, fo_ = sc.get("lock_at", 1.6), sc.get("follow_at", 4.5)
    before = draw_borders(img, sc, t, tg, a)
    yr = "1913" if before else "1914"
    text_a(img, (W / 2, 330), yr, F("anton", 96), T["accent"] if before else T["alert"], a, "mm", shadow=8)
    lab = "FREE TO TRAVEL" if before else "PASSPORT REQUIRED"
    f = F("anton", 84); w = ImageDraw.Draw(img).textlength(lab, font=f); pa = 1.0 if before else ease(clamp((t - la_) / 0.3))
    rect_a(img, (W / 2 - w / 2 - 34, 1110, W / 2 + w / 2 + 34, 1230), (T["accent2"] if before else T["alert"]), 0.92 * a * pa, 18)
    text_a(img, (W / 2, 1170), lab, f, (14, 10, 6), a * pa, "mm")
    for i, ln in enumerate(sc.get("lines", [])):
        st = la_ + 0.6 + i * (max(0.8, fo_ - la_ - 0.6) if i else 0)
        rise_line(img, ln, W / 2, 1320 + i * 72, fit_font("disp", 50, ln, W - 120, "Bold"), t - st)
    chrome(img, tg, a)

R.SCENE_FN.update({"booklet": sc_booklet, "timeline": sc_timeline, "borders": sc_borders})

# ------------------------------------------------------------------ fingerprint scenes (reel 013)
_fp = {}
def fp_field(w, h, seed=1, kind="whorl"):
    """Synthetic fingerprint ridge intensity in 0..1 (whorl or arch), inside a soft oval."""
    key = (w, h, seed, kind)
    if key in _fp: return _fp[key]
    r = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    x = (xx - w * 0.5) / (w * 0.5); y = (yy - h * 0.55) / (h * 0.5)
    wx = sum(r.uniform(.02, .05) * np.sin(r.uniform(2, 5) * y + r.uniform(0, 6)) for _ in range(3))
    wy = sum(r.uniform(.02, .05) * np.sin(r.uniform(2, 5) * x + r.uniform(0, 6)) for _ in range(3))
    X, Y = x + wx + r.uniform(-.06, .06), y + wy + r.uniform(-.06, .06)
    if kind == "whorl":
        f = np.sqrt((X * 1.08) ** 2 + (Y * 0.92) ** 2) + 0.03 * np.arctan2(Y, X)
    elif kind == "loop":                                                  # U-shaped ridges around a core, exiting to one side
        x0, y0 = 0.05, -0.05; r_ = np.sqrt((X - x0) ** 2 + (Y - y0) ** 2)
        f = np.where(Y < y0, r_, np.abs(X - x0 + 0.9 * (Y - y0)))
        arch = Y * 0.9 + 0.35 * np.exp(-(X ** 2) * 3.0) * (1.0 - np.clip(Y + 0.4, 0, 2) * 0.5)
        w_ = np.clip((r_ - 0.55) / 0.15, 0, 1); f = f * (1 - w_) + (arch + 0.6) * w_
    else:
        f = Y * 0.9 + 0.35 * np.exp(-(X ** 2) * 3.0) * (1.0 - np.clip(Y + 0.4, 0, 2) * 0.5)
    rid = 0.5 + 0.5 * np.cos(2 * math.pi * f * r.uniform(10.5, 12.5))
    rid = np.clip((rid - 0.38) * 2.6, 0, 1)
    br = r.random((h // 6 + 1, w // 6 + 1)) > 0.06                       # small breaks = minutiae
    rid *= np.kron(br, np.ones((6, 6)))[:h, :w]
    m = np.clip((1 - ((x / 0.88) ** 2 + (y / 1.0) ** 2)) * 7, 0, 1)
    out = (rid * m).astype(np.float32); _fp[key] = out; return out

def fp_img(w, h, seed, col, alpha=1.0, kind="whorl"):
    f = fp_field(w, h, seed, kind); a = (f * 255 * alpha).astype(np.uint8)
    im = Image.new("RGBA", (w, h), col + (0,)); im.putalpha(Image.fromarray(a)); return im

MINU = [(0.38, 0.30), (0.62, 0.36), (0.30, 0.55), (0.55, 0.52), (0.70, 0.66), (0.44, 0.74)]

def draw_fingerprint(img, sc, t, xl, xr, y0):
    """Evidence card at x=xl, record search card at x=xr (each 460x650), top at y0. Returns fade alpha."""
    a = ease(clamp(t / 0.5)); seed = sc.get("seed", 7)
    cw, chh = 460, 650
    pw, ph = 340, 440
    sa = sc.get("scan_at", 0.6); ma = sc.get("match_at")
    # evidence card (paper + blood print)
    card = paper(cw, chh).copy(); d = ImageDraw.Draw(card)
    d.text((24, 22), sc.get("left_label", "EVIDENCE"), font=F("mono", 22), fill=(110, 40, 30))
    card.alpha_composite(fp_img(pw, ph, seed, (150, 24, 20), 0.92), ((cw - pw) // 2, 90))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, chh), (0, 0, 0, 170)); lay.alpha_composite(sh, (xl + 14, int(y0 + 20)))
    lay = lay.filter(ImageFilter.GaussianBlur(14)); lay.alpha_composite(card.rotate(-3, expand=False, resample=Image.BICUBIC), (xl, int(y0)))
    paste_a(img, lay, ((1 - a) * -200, 0), a)
    px, py = xl + (cw - pw) // 2, y0 + 90
    sp = clamp((t - sa) / 1.4)
    if 0 < sp < 1:                                                       # scan beam
        by = py + ph * sp
        rect_a(img, (xl + 10, by - 3, xl + cw - 10, by + 3), T["accent"], 0.9)
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).rectangle([xl, by - 40, xl + cw, by + 40], fill=T["accent"] + (70,))
        img.alpha_composite(g.filter(ImageFilter.GaussianBlur(20)))
    if sp > 0:                                                           # scanned part glows cyan
        cy_ = fp_img(pw, ph, seed, T["accent"], 0.55)
        crop = cy_.crop((0, 0, pw, max(1, int(ph * sp)))); img.alpha_composite(crop, (int(px), int(py)))
    d = ImageDraw.Draw(img)
    if sp >= 1:
        for j, (mx, my) in enumerate(MINU):
            q = clamp((t - sa - 1.4 - j * 0.12) / 0.3)
            if q > 0:
                cx_, cy2 = px + mx * pw, py + my * ph; rr = 16
                d.ellipse([cx_ - rr, cy2 - rr, cx_ + rr, cy2 + rr], outline=T["accent2"] + (int(255 * q),), width=3)
    # record search (right)
    if ma is not None:
        st = sc.get("search_at", max(sa + 1.6, ma - 2.2)); rp = clamp((t - st) / 0.4)
        if rp > 0:
            rc = Image.new("RGBA", (cw, chh), (18, 26, 30, 240)); rd = ImageDraw.Draw(rc)
            rd.rectangle([2, 2, cw - 3, chh - 3], outline=T["accent"] + (160,), width=2)
            rd.text((24, 22), "RECORD SEARCH", font=F("mono", 22), fill=T["accent"] + (255,))
            matched = t >= ma
            s2 = seed if matched else 100 + int((t - st) / 0.11) % 40
            rc.alpha_composite(fp_img(pw, ph, s2, (230, 236, 236), 0.9, "whorl" if (s2 % 3 or matched) else "arch"), ((cw - pw) // 2, 90))
            lab = sc.get("right_label", "MATCH") if matched else f"CARD #{(int((t - st) * 97) % 7000) + 1:04d}"
            rd.text((cw / 2, chh - 40), lab, font=fit_font("mono", 26, lab, cw - 40), fill=(T["accent2"] if matched else MUTED) + (255,), anchor="mm")
            paste_a(img, rc, (xr + (1 - rp) * 200, y0), rp)
            if matched:
                q = ease(clamp((t - ma) / 0.5)); d = ImageDraw.Draw(img); rx = xr + (cw - pw) // 2
                for (mx, my) in MINU:
                    x1, y1 = px + mx * pw, py + my * ph; x2, y2 = rx + mx * pw, py + my * ph
                    d.line([x1, y1, x1 + (x2 - x1) * q, y1 + (y2 - y1) * q], fill=T["accent2"] + (200,), width=3)
                    if q >= 1: d.ellipse([x2 - 16, y2 - 16, x2 + 16, y2 + 16], outline=T["accent2"] + (255,), width=3)
                zp = clamp((t - ma - 0.4) / 0.18)
                if zp > 0:
                    stp = stamp_img(sc.get("stamp", "MATCH"), col=(60, 220, 140), size=88); z = 2.2 - 1.2 * ease(zp)
                    stp = stp.resize((int(stp.width * z), int(stp.height * z)), Image.LANCZOS).rotate(-10, expand=True, resample=Image.BICUBIC)
                    img.alpha_composite(stp, (int((xl + cw + xr) / 2 - stp.width / 2), int(y0 + chh - 40 - stp.height / 2)))
    return a

def sc_fingerprint(img, sc, t, D, tg, k):
    """Evidence print on an old almanac page is scanned; a record card search flickers until it MATCHES."""
    a = draw_fingerprint(img, sc, t, 56, W - 56 - 460, sc.get("y", 370))
    caption(img, sc, t + sc.get("cap_lead", 0.0), D, sc.get("cap_y", 1110))
    chrome(img, tg, a)

FVAL = [16, 16, 8, 8, 4, 4, 2, 2, 1, 1]
FNAME = ["R THUMB", "R INDEX", "R MIDDLE", "R RING", "R LITTLE", "L THUMB", "L INDEX", "L MIDDLE", "L RING", "L LITTLE"]
def sc_drawers(img, sc, t, D, tg, k):
    """The Haque-Bose primary classification: whorl fingers light up with 16/8/4/2/1, a fraction forms, one drawer of 1,024 opens."""
    a = clamp(t / 0.4)
    text_a(img, (W / 2, 300), typed(sc.get("kicker", ""), prog(t, 0.1, 0.6)), F("mono", 32), T["accent"], 1, "mm", shadow=4)
    wh = sc.get("whorls", [1, 4, 7]); fat = sc.get("finger_at", [1.0 + i * 0.6 for i in range(len(wh))])
    tw_, gap = 172, 16; x0 = (W - (5 * tw_ + 4 * gap)) / 2
    d = ImageDraw.Draw(img)
    for i in range(10):
        r_, c_ = divmod(i, 5); x = x0 + c_ * (tw_ + gap); y = 350 + r_ * 215; ap = clamp((t - 0.2 - i * 0.05) / 0.3) * a
        n = i + 1; on = n in wh and t >= fat[wh.index(n)]
        col = T["accent"] if on else (60, 80, 86)
        rect_a(img, (x, y, x + tw_, y + 200), (14, 24, 28), 0.9 * ap, 12)
        d.rounded_rectangle([x, y, x + tw_, y + 200], 12, outline=col + (int(255 * ap),), width=3 if on else 2)
        fi = fp_img(96, 122, 30 + i, (WHITE if on else (110, 120, 120)), (1.0 if on else 0.5) * ap, "whorl" if n in wh else "arch")
        img.alpha_composite(fi, (int(x + (tw_ - 96) / 2), int(y + 30)))
        text_a(img, (x + tw_ / 2, y + 16), FNAME[i], F("mono", 17), MUTED, ap, "mm")
        v = f"{FVAL[i]}" if on else "0"
        text_a(img, (x + tw_ / 2, y + 176), v, F("anton", 40), T["accent2"] if on else (90, 100, 100), ap, "mm")
        if on and t - fat[wh.index(n)] < 0.6:
            rr = 30 + 160 * (t - fat[wh.index(n)]); d.ellipse([x + tw_ / 2 - rr, y + 92 - rr, x + tw_ / 2 + rr, y + 92 + rr], outline=T["accent"] + (int(200 * (1 - (t - fat[wh.index(n)]) / 0.6)),), width=3)
    fa = sc.get("formula_at", fat[-1] + 0.8); fp = ease(clamp((t - fa) / 0.6))
    num = [FVAL[n - 1] for n in wh if n % 2 == 0]; den = [FVAL[n - 1] for n in wh if n % 2 == 1]
    N, Dn = 1 + sum(num), 1 + sum(den)
    if fp > 0:
        ns = " + ".join(["1"] + [str(v) for v in num]); ds = " + ".join(["1"] + [str(v) for v in den])
        text_a(img, (330, 845), ns, F("anton", 58), WHITE, fp, "mm", shadow=6)
        rect_a(img, (150, 884, 510, 890), T["accent"], fp)
        text_a(img, (330, 930), ds, F("anton", 58), WHITE, fp, "mm", shadow=6)
        text_a(img, (580, 888), "=", F("anton", 90), MUTED, fp, "mm")
        text_a(img, (800, 888), f"{N}/{Dn}", F("anton", 150), T["accent2"], fp, "mm", shadow=10)
    ga = ease(clamp((t - fa - 0.6) / 0.8)); da = sc.get("drawer_at", fa + 2.2)
    if ga > 0:
        text_a(img, (W / 2, 1030), "32 × 32 = 1,024 DRAWERS", F("mono", 30), T["accent"], ga, "mm")
        cs, cg = 13, 2; gx = (W - 32 * (cs + cg)) / 2; gy = 1060
        hr, hc = Dn - 1, N - 1; op = ease(clamp((t - da) / 0.5))
        for rr_ in range(32):
            for cc in range(32):
                if (rr_ + cc) / 62 > ga: continue
                xx, yy = gx + cc * (cs + cg), gy + rr_ * (cs + cg)
                hit = (rr_ == hr and cc == hc)
                fill = (T["accent2"] + (255,)) if (hit and op > 0) else (70, 130, 138, 255) if (rr_ == hr or cc == hc) and op > 0 else (40, 72, 80, 255)
                d.rectangle([xx, yy, xx + cs, yy + cs], fill=fill)
        if op > 0:
            xx, yy = gx + hc * (cs + cg) + cs / 2, gy + hr * (cs + cg) + cs / 2
            rr = 14 + 10 * math.sin(tg * 6); d.ellipse([xx - rr, yy - rr, xx + rr, yy + rr], outline=T["accent2"] + (255,), width=3)
            text_a(img, (min(W - 140, xx + 40), yy - 4), f"DRAWER {N}/{Dn}", F("mono", 26), T["accent2"], op, "lm", shadow=6)
    for i, ln in enumerate(sc.get("lines", [])):
        rise_line(img, ln, W / 2, 1560 + i * 66, fit_font("disp", 46 if i == 0 else 40, ln, W - 120, "Black" if i == 0 else "Bold"), t - (da + 0.4 + i * 0.6))
    chrome(img, tg, a)

_world = {}
WD = dict(c_lat=12.0, c_lon=30.0, s=4.0, cx=W / 2, cy=660)
def _wp(lat, lon): return WD["cx"] + (lon - WD["c_lon"]) * WD["s"], WD["cy"] - (lat - WD["c_lat"]) * WD["s"]
def _world_img():
    if "img" not in _world:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        for iso, rings in R.COUNTRIES:
            for ring in rings:
                pts = [_wp(la, lo) for lo, la in zip(np.degrees(ring[:, 0]), np.degrees(ring[:, 1]))]
                if max(abs(p[0] - pts[0][0]) for p in pts) > W * 0.8: continue   # skip dateline-wrapping rings
                d.polygon(pts, fill=T["land"] + (255,), outline=T["land"] + (255,))
        glow = Image.new("RGBA", (W, H), T["accent"] + (0,)); glow.putalpha(lay.getchannel("A").filter(ImageFilter.GaussianBlur(5)).point(lambda v: int(v * 0.45)))
        out = Image.new("RGBA", (W, H), (0, 0, 0, 0)); out.alpha_composite(glow); out.alpha_composite(lay); _world["img"] = out
    return _world["img"]

def draw_spread(img, sc, t, tg, a):
    """World map + arcs; returns the year label for the latest route that has started."""
    paste_a(img, _world_img(), (0, 0), a); d = ImageDraw.Draw(img)
    on, ola, olo = sc["origin"]; ox, oy = _wp(ola, olo); pos = {on: (ox, oy)}
    year = sc.get("year0", "")
    for nm, la, lo, at, *rest in sc["routes"]:
        fr = rest[0] if rest and rest[0] else on; x1, y1 = pos.get(fr, (ox, oy)); x2, y2 = _wp(la, lo); pos[nm] = (x2, y2)
        p = ease(clamp((t - at) / 0.9))
        if p <= 0: continue
        if len(rest) > 1 and rest[1]: year = rest[1]
        mx, my = (x1 + x2) / 2, min(y1, y2) - abs(x2 - x1) * 0.28 - 30
        pts = [((1 - u) ** 2 * x1 + 2 * (1 - u) * u * mx + u * u * x2, (1 - u) ** 2 * y1 + 2 * (1 - u) * u * my + u * u * y2) for u in np.linspace(0, p, 40)]
        d.line(pts, fill=T["accent2"] + (230,), width=4)
        hx, hy = pts[-1]; d.ellipse([hx - 7, hy - 7, hx + 7, hy + 7], fill=(255, 255, 255, 255))
        if p >= 1:
            q = t - at - 0.9; rr = 10 + (q * 30 % 30)
            d.ellipse([x2 - rr, y2 - rr, x2 + rr, y2 + rr], outline=T["accent2"] + (int(220 * (1 - (rr - 10) / 30)),), width=3)
            d.ellipse([x2 - 9, y2 - 9, x2 + 9, y2 + 9], fill=T["accent2"] + (255,))
            anc = "rm" if x2 > W - 220 else "lm"; text_a(img, (x2 + (-16 if anc == "rm" else 16), y2 - 24), nm, F("mono", 24), WHITE, clamp(q / 0.3), anc, shadow=6)
    rr = 12 + 8 * math.sin(tg * 5); d.ellipse([ox - rr, oy - rr, ox + rr, oy + rr], outline=T["accent"] + (255,), width=4)
    d.ellipse([ox - 9, oy - 9, ox + 9, oy + 9], fill=T["accent"] + (255,))
    text_a(img, (ox + 16, oy + 26), on, F("mono", 26), T["accent"], a, "lm", shadow=6)
    return year

def sc_spread(img, sc, t, D, tg, k):
    """Arcs fly from an origin city to destinations one by one (origin [name, lat, lon]; routes [[name, lat, lon, at, from?, year]])."""
    a = clamp(t / 0.5); year = draw_spread(img, sc, t, tg, a)
    text_a(img, (W / 2, 330), year, F("anton", 110), T["accent2"], a, "mm", shadow=8)
    caption(img, sc, t, D, sc.get("cap_y", 1000))
    chrome(img, tg, a)

R.SCENE_FN.update({"fingerprint": sc_fingerprint, "drawers": sc_drawers, "spread": sc_spread})

R.SCENE_FN.update({"satellite": sc_satellite, "map": sc_map, "dossier": sc_dossier, "blast": sc_blast})
R.SCENE_FN.update({"iceberg": sc_iceberg})
R.SCENE_FN.update({"photo": sc_photo, "counter": sc_counter, "bulb": sc_bulb})

# ---------------------------------------------------------------- payments scenes (reel 015: UPI)
def qr_img(n, s, seed=3, fg=(16, 18, 20), bg=(250, 250, 246)):
    """Illustrative QR-style code (random modules + finder squares; not a real, scannable code)."""
    r = np.random.default_rng(seed); m = r.random((n, n)) > 0.52
    for (cy, cx) in [(0, 0), (0, n - 7), (n - 7, 0)]:
        m[cy:cy + 7, cx:cx + 7] = False
        m[cy, cx:cx + 7] = m[cy + 6, cx:cx + 7] = m[cy:cy + 7, cx] = m[cy:cy + 7, cx + 6] = True
        m[cy + 2:cy + 5, cx + 2:cx + 5] = True
        m[cy + 1:cy + 6, cx + 1] = m[cy + 1:cy + 6, cx + 5] = m[cy + 1, cx + 1:cx + 6] = m[cy + 5, cx + 1:cx + 6] = False
    q = Image.new("RGBA", (n + 4, n + 4), bg + (255,)); px = q.load()
    for y in range(n):
        for x in range(n):
            if m[y, x]: px[x + 2, y + 2] = fg + (255,)
    return q.resize((s, s), Image.NEAREST)

def tick_mark(d, cx, cy, s, col, w):
    d.line([cx - 0.45 * s, cy, cx - 0.12 * s, cy + 0.32 * s, cx + 0.5 * s, cy - 0.36 * s], fill=col, width=w, joint="curve")

def sc_scanpay(img, sc, t, D, tg, k):
    """Hook: a phone scans a shop QR, payment succeeds with a ripple, then the monthly UPI count ticks up."""
    a = ease(clamp(t / 0.5)); pw, ph = 360, 640; px0 = W / 2 - pw / 2; py0 = 330 + 120 * (1 - a)
    pay = sc.get("pay_at", 1.9); cnt = sc.get("count_at", pay + 0.6)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([px0 + 16, py0 + 26, px0 + pw + 16, py0 + ph + 26], 54, fill=(0, 0, 0, 150))
    lay = lay.filter(ImageFilter.GaussianBlur(18)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([px0, py0, px0 + pw, py0 + ph], 54, fill=(18, 18, 22, 255), outline=T["accent"] + (200,), width=4)
    d.rounded_rectangle([px0 + 18, py0 + 60, px0 + pw - 18, py0 + ph - 40], 26, fill=(250, 250, 246, 255))
    d.rounded_rectangle([px0 + pw / 2 - 50, py0 + 22, px0 + pw / 2 + 50, py0 + 36], 7, fill=(40, 40, 46, 255))
    paid = t >= pay
    if not paid:
        q = qr_img(25, 250); lay.alpha_composite(q, (int(px0 + pw / 2 - 125), int(py0 + 150)))
        d.text((px0 + pw / 2, py0 + 110), "SCAN & PAY", font=F("disp", 34, "Black"), fill=(20, 20, 24, 255), anchor="mm")
        d.text((px0 + pw / 2, py0 + 450), "CHAI STALL · ₹10", font=F("inter", 28, "Bold"), fill=(90, 90, 96, 255), anchor="mm")
        sp = clamp((t - 0.55) / 1.1)
        if 0 < sp < 1:
            by = py0 + 150 + 250 * (0.5 - 0.5 * math.cos(sp * math.pi * 2))
            d.rectangle([px0 + 40, by - 3, px0 + pw - 40, by + 3], fill=T["accent2"] + (255,))
    else:
        q = ease(clamp((t - pay) / 0.35)); cx, cy = px0 + pw / 2, py0 + 270
        d.ellipse([cx - 110 * q, cy - 110 * q, cx + 110 * q, cy + 110 * q], fill=(40, 186, 110, 255))
        if q > 0.6: tick_mark(d, cx, cy, 140, (255, 255, 255, 255), 16)
        al = int(255 * clamp((t - pay - 0.2) / 0.3))
        d.text((cx, py0 + 450), "₹10 PAID", font=F("anton", 64), fill=(20, 20, 24, al), anchor="mm")
        d.text((cx, py0 + 515), "in 2 seconds", font=F("inter", 28, "Bold"), fill=(90, 90, 96, al), anchor="mm")
    img.alpha_composite(lay)
    if paid:                                                             # sound-box ripple
        dd = ImageDraw.Draw(img); cx, cy = W / 2, py0 + 270
        for j in range(3):
            rp = (t - pay - j * 0.25)
            if 0 < rp < 1.4:
                rr = 140 + rp * 380; al = int(200 * (1 - rp / 1.4))
                dd.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=T["accent2"] + (al,), width=5)
    ca = clamp((t - cnt) / 0.3); p = ease(clamp((t - cnt) / 1.6))
    if ca > 0:
        text_a(img, (W / 2, 1040), typed(sc.get("kicker", ""), prog(t, cnt, 0.5)), F("mono", 32), T["accent"], 1, "mm", shadow=4)
        num = sc.get("number", "25.47 BILLION"); val = float(num.split()[0]); unit = " ".join(num.split()[1:])
        s = f"{val * p:.2f} {unit}" if p < 1 else num
        text_a(img, (W / 2, 1160), s, F("anton", 150), WHITE, ca, "mm", shadow=12)
        text_a(img, (W / 2, 1265), sc.get("label", ""), fit_font("disp", 46, sc.get("label", ""), W - 140, "Black"), T["accent2"], ca, "mm")
    for i, ln in enumerate(sc.get("lines", [])):
        rise_line(img, ln, W / 2, 1370 + i * 70, fit_font("disp", 54, ln, W - 120, "Bold"), t - sc.get("lines_at", cnt + 1.2) - i * 0.5)
    chrome(img, tg, a)

def key_icon(w, col):
    im = Image.new("RGBA", (w, w // 2), (0, 0, 0, 0)); d = ImageDraw.Draw(im); h = w // 2; r = h * 0.36
    d.ellipse([6, h / 2 - r, 6 + 2 * r, h / 2 + r], outline=col, width=max(4, w // 22))
    d.line([6 + 2 * r, h / 2, w - 8, h / 2], fill=col, width=max(5, w // 18))
    for x in (w - 30, w - 58):
        d.line([x, h / 2, x, h / 2 + h * 0.28], fill=col, width=max(5, w // 18))
    return im

def sc_keys(img, sc, t, D, tg, k):
    """Premise: a padlock with three keyholes; two keys are the popular answer, the third is a mystery."""
    a = ease(clamp(t / 0.4)); kat = sc.get("key_at", [0.6, 1.6, 3.2]); cx = W / 2
    d = ImageDraw.Draw(img)
    sh = 0 if t < kat[2] else 6 * math.sin((t - kat[2]) * 30) * max(0, 1 - (t - kat[2]) / 0.6)
    bx0, by0, bx1, by1 = cx - 260 + sh, 470, cx + 260 + sh, 830
    d.arc([cx - 170 + sh, 300, cx + 170 + sh, 640], 180, 360, fill=(170, 170, 160, int(255 * a)), width=34)
    d.line([cx - 170 + sh, 470, cx - 170 + sh, 485], fill=(170, 170, 160, int(255 * a)), width=34)
    d.line([cx + 170 + sh, 470, cx + 170 + sh, 485], fill=(170, 170, 160, int(255 * a)), width=34)
    rect_a(img, (bx0, by0, bx1, by1), (58, 50, 30), a, 40, T["accent"], 4)
    for i in range(3):
        hx = cx + sh + (i - 1) * 150; hy = 640; on = t >= kat[i]
        col = (T["accent2"] if i < 2 else T["alert"]) if on else (20, 18, 12)
        if on and i == 2 and int(t * 4) % 2: col = (255, 150, 140)
        d.ellipse([hx - 26, hy - 44, hx + 26, hy + 8], fill=col + (255,))
        d.polygon([(hx - 16, hy), (hx + 16, hy), (hx + 26, hy + 70), (hx - 26, hy + 70)], fill=col + (255,))
    tw, th, gap = 300, 230, 30; x0 = cx - (3 * tw + 2 * gap) / 2
    for i, (lab, sub) in enumerate(sc.get("keys", [])):
        q = ease(clamp((t - kat[i]) / 0.4))
        if q <= 0: continue
        x = x0 + i * (tw + gap); y = 900 + 60 * (1 - q); mystery = (lab == "?")
        rect_a(img, (x, y, x + tw, y + th), (30, 26, 16) if not mystery else (50, 16, 16), q * 0.92, 26, T["alert"] if mystery else T["accent"], 3)
        if mystery:
            text_a(img, (x + tw / 2, y + 100), "?", F("anton", 140), T["alert"], q, "mm", shadow=6)
        else:
            ki = key_icon(160, T["accent2"] + (255,)); paste_a(img, ki, (x + tw / 2 - 80, y + 26), q)
            text_a(img, (x + tw / 2, y + 140), lab, fit_font("anton", 66, lab, tw - 30), WHITE, q, "mm", shadow=4)
        text_a(img, (x + tw / 2, y + 200), sub, fit_font("inter", 28, sub, tw - 30, "Bold"), MUTED if not mystery else (255, 160, 150), q, "mm")
    text_a(img, (W / 2, 1220), typed(sc.get("kicker", ""), prog(t, 0.2, 0.5)), F("mono", 32), T["accent"], 1, "mm", shadow=4)
    for i, ln in enumerate(sc.get("lines", [])):
        rise_line(img, ln, W / 2, 1320 + i * 72, fit_font("disp", 58, ln, W - 120, "Bold"), t - kat[min(i + 1, 2)])
    chrome(img, tg, a)

def sc_pricefall(img, sc, t, D, tg, k):
    """Data price per GB: a tall 2016 bar collapses to today's sliver; then data use per person shoots up."""
    a = ease(clamp(t / 0.4)); da = sc.get("drop_at", 2.5); ua = sc.get("use_at", da + 2.0)
    text_a(img, (W / 2, 330), typed(sc.get("kicker", ""), prog(t, 0.1, 0.5)), F("mono", 32), T["accent"], 1, "mm", shadow=4)
    text_a(img, (W / 2, 392), sc.get("plabel", ""), F("disp", 40, "Black"), MUTED, a, "mm")
    base = 960; hmax = 400; p0, p1 = sc["p0"], sc["p1"]
    g0 = ease(clamp((t - 0.3) / 0.8)); h0 = hmax * g0
    rect_a(img, (190, base - h0, 450, base), T["alert"], a, 16)
    text_a(img, (320, base - h0 - 60), f"₹{int(p0 * g0)}", F("anton", 96), WHITE, g0, "mm", shadow=8)
    text_a(img, (320, base + 50), "2015–16", F("disp", 40, "Black"), MUTED, a, "mm")
    q = ease(clamp((t - da) / 0.55)); h1 = hmax * (p0 + (p1 - p0) * q) / p0
    if t >= da - 0.01:
        cc = tuple(int(T["alert"][j] + (T["accent2"][j] - T["alert"][j]) * q) for j in range(3))
        rect_a(img, (630, base - h1, 890, base), cc, 1, 16)
        v = p0 + (p1 - p0) * q
        text_a(img, (760, base - h1 - 60), f"₹{v:.1f}" if q >= 1 else f"₹{int(v)}", F("anton", 96), cc, 1, "mm", shadow=8)
        text_a(img, (760, base + 50), "TODAY", F("disp", 40, "Black"), MUTED, q, "mm")
        if q >= 1:
            ca = back(clamp((t - da - 0.55) / 0.4)); s = "−97%"
            f = F("anton", int(88 * clamp(ca, 0, 1.2))) if ca > 0.05 else None
            if f: rect_a(img, (585, 640, 935, 780), T["alert"], clamp((t - da - 0.55) / 0.2), 24); text_a(img, (760, 710), s, f, WHITE, 1, "mm")
    else:
        rect_a(img, (630, base - 4, 890, base), (70, 70, 60), a, 2)
    rect_a(img, (150, base, W - 150, base + 4), (120, 110, 80), a)
    u = ease(clamp((t - ua) / 1.2))
    if t >= ua:
        text_a(img, (W / 2, 1100), sc.get("ulabel", ""), F("disp", 38, "Black"), MUTED, clamp((t - ua) / 0.3), "mm")
        rect_a(img, (120, 1150, W - 120, 1210), (40, 38, 30), 0.9, 30)
        u0, u1 = sc["u0"], sc["u1"]; v = u0 + (u1 - u0) * u
        rect_a(img, (120, 1150, 120 + max(30, (W - 240) * v / u1), 1210), T["accent"], 1, 30)
        text_a(img, (W / 2, 1270), f"{u0} GB  →  {v:.1f} GB", F("anton", 64), WHITE, clamp((t - ua) / 0.3), "mm", shadow=6)
    for i, ln in enumerate(sc.get("lines", [])):
        rise_line(img, ln, W / 2, 1380 + i * 70, fit_font("disp", 58, ln, W - 120, "Bold"), t - ua - 1.4)
    chrome(img, tg, a)

def shop_icon(w, qr=0.0, lit=0.0, seed=0):
    h = int(w * 0.9); im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    st = 6; aw = h * 0.3
    for j in range(st):
        x0 = j * w / st; col = (T["accent"] if j % 2 == 0 else (240, 236, 224)) if lit > 0.5 else ((120, 100, 50) if j % 2 == 0 else (110, 108, 100))
        d.polygon([(x0, 0), (x0 + w / st, 0), (x0 + w / st + 2, aw), (x0 - 2, aw)], fill=col + (255,))
    d.rectangle([w * 0.06, aw, w * 0.94, h - 2], fill=(46, 40, 30, 255) if lit > 0.5 else (34, 32, 28, 255))
    d.rectangle([w * 0.06, h * 0.68, w * 0.94, h * 0.76], fill=(80, 64, 40, 255))
    if qr > 0:
        s = int(w * 0.38 * clamp(back(qr), 0, 1.2))
        if s > 4: im.alpha_composite(qr_img(15, s, seed), (int(w / 2 - s / 2), int(aw + (h * 0.66 - aw) / 2 - s / 2 + 4)))
    return im

def sc_qrshops(img, sc, t, D, tg, k):
    """A town of stalls; QR stickers pop from the centre outward (no card machine needed)."""
    a = ease(clamp(t / 0.4)); qa = sc.get("qr_at", 1.0); ca = sc.get("count_at", qa + 2.4)
    cols, rows, cw = 6, 4, 150; gx = W / 2 - cols * (cw + 14) / 2; gy = 340
    for r_ in range(rows):
        for c in range(cols):
            dist = math.hypot(c - (cols - 1) / 2, (r_ - (rows - 1) / 2) * 1.1)
            q = clamp((t - qa - dist * 0.32) / 0.35)
            ic = shop_icon(cw, q, q, seed=r_ * cols + c)
            paste_a(img, ic, (gx + c * (cw + 14), gy + r_ * (cw * 0.9 + 18)), a * (0.55 + 0.45 * (q > 0)))
    if t >= ca:
        cq = clamp((t - ca) / 0.3); p = ease(clamp((t - ca) / 1.0)); v = 5 + 5 * p
        rect_a(img, (W / 2 - 330, 975, W / 2 + 330, 1125), (14, 40, 26), cq * 0.95, 28, T["accent2"], 3)
        text_a(img, (W / 2, 1030), f"5 LAKH → {v:.0f} LAKH", F("anton", 84), WHITE, cq, "mm", shadow=6)
        text_a(img, (W / 2, 1095), "PAYTM MERCHANTS · SEPT → NOV 2016", F("inter", 28, "Bold"), T["accent2"], cq, "mm")
    caption(img, sc, t, D, 1190)
    chrome(img, tg, a)

def sc_network(img, sc, t, D, tg, k):
    """UPI: every bank on the left, every app on the right, joined through one switch in the middle."""
    a = ease(clamp(t / 0.4)); la = sc.get("link_at", 1.6); hx, hy = W / 2, 690
    banks, apps = sc.get("banks", []), sc.get("apps", [])
    ys = [400 + i * 145 for i in range(5)]
    d = ImageDraw.Draw(img); lp = ease(clamp((t - la) / 0.9))
    for side, items in ((0, banks), (1, apps)):
        for i, lab in enumerate(items):
            y = ys[i]; x0 = 70 if side == 0 else W - 70 - 300
            ex = x0 + 300 if side == 0 else x0
            if lp > 0:
                x2 = ex + (hx - ex) * lp; y2 = y + (hy - y) * lp
                d.line([ex, y, x2, y2], fill=T["accent2"] + (200,), width=4)
                if lp >= 1:
                    for j in range(2):
                        f = ((tg * 0.9 + i * 0.37 + j * 0.5 + side * 0.2) % 1.0)
                        f = f if side == 0 else 1 - f
                        px = ex + (hx - ex) * f; py = y + (hy - y) * f
                        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=T["accent"] + (255,))
            q = ease(clamp((t - 0.2 - i * 0.1 - side * 0.3) / 0.4))
            first = (side == 0 and i == 0)
            rect_a(img, (x0, y - 50, x0 + 300, y + 50), (40, 34, 20) if first else (26, 26, 24), q * 0.95, 20,
                   T["accent"] if (first or lp > 0) else (90, 90, 84), 3)
            f = fit_font("disp" if not first else "anton", 44 if not first else 50, lab, 270, "Black" if not first else None)
            text_a(img, (x0 + 150, y), lab, f, WHITE if (first or lp > 0) else MUTED, q, "mm")
    text_a(img, (225, 330), "BANKS", F("mono", 28), MUTED, a, "mm"); text_a(img, (W - 225, 330), "APPS", F("mono", 28), MUTED, a, "mm")
    g = ease(clamp((t - la + 0.3) / 0.6))
    if g > 0:
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse([hx - 170, hy - 170, hx + 170, hy + 170], fill=T["accent"] + (int(120 * g),))
        img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(40)))
        rr = 105 * clamp(back((t - la + 0.3) / 0.6), 0, 1.15)
        d = ImageDraw.Draw(img); d.ellipse([hx - rr, hy - rr, hx + rr, hy + rr], fill=(24, 20, 10, 255), outline=T["accent"] + (255,), width=6)
        text_a(img, (hx, hy - 6), sc.get("hub", "UPI"), F("anton", int(86 * clamp(rr / 105, 0, 1))), T["accent"], g, "mm", shadow=6)
    caption(img, sc, t, D, 1160)
    chrome(img, tg, a)

def sc_share(img, sc, t, D, tg, k):
    """Market share bars; the highlighted app pulses; a chip explains the fall."""
    a = ease(clamp(t / 0.4)); ba = sc.get("bars_at", 0.5); ha = sc.get("hl_at", ba + 1.6); cha = sc.get("chip_at", ha + 1.2)
    text_a(img, (W / 2, 330), typed(sc.get("kicker", ""), prog(t, 0.1, 0.5)), F("mono", 32), T["accent"], 1, "mm", shadow=4)
    x0, xm = 330, W - 150; sc_max = 50.0
    for i, (lab, v) in enumerate(sc.get("bars", [])):
        y = 470 + i * 150; q = ease(clamp((t - ba - i * 0.25) / 0.8)); hl = (lab == sc.get("hl"))
        col = T["alert"] if (hl and t >= ha) else (T["accent"] if i < 2 else (120, 116, 100))
        text_a(img, (x0 - 24, y), lab, fit_font("disp", 50, lab, 260, "Black"), WHITE if (not hl or t < ha) else T["alert"], clamp((t - ba - i * 0.25) / 0.3), "rm")
        bw = (xm - x0) * v / sc_max * q
        rect_a(img, (x0, y - 42, x0 + max(8, bw), y + 42), col, clamp((t - ba - i * 0.25) / 0.3), 14)
        text_a(img, (x0 + bw + 20, y), f"{v * q:.1f}%", F("anton", 60), WHITE, clamp((t - ba - i * 0.25) / 0.3), "lm", shadow=4)
        if hl and t >= ha:
            pa = 0.5 + 0.5 * math.sin((t - ha) * 6)
            rect_a(img, (x0 - 290, y - 58, xm + 40, y + 58), None, 0.5 + 0.5 * pa, 20, T["alert"], 4)
    if t >= cha:
        q = back(clamp((t - cha) / 0.45)); s = sc.get("chip", "")
        f = fit_font("disp", 50, s, W - 220, "Black"); w = ImageDraw.Draw(img).textlength(s, font=f)
        rect_a(img, (W / 2 - w / 2 - 34, 1060, W / 2 + w / 2 + 34, 1160), T["alert"], clamp((t - cha) / 0.2), 26)
        text_a(img, (W / 2, 1110), s, f, WHITE, clamp((t - cha) / 0.2), "mm")
    for i, ln in enumerate(sc.get("lines", [])):
        rise_line(img, ln, W / 2, 1260 + i * 70, fit_font("disp", 48, ln, W - 120, "Bold"), t - cha - 0.5)
    chrome(img, tg, a)

R.SCENE_FN.update({"scanpay": sc_scanpay, "keys": sc_keys, "pricefall": sc_pricefall, "qrshops": sc_qrshops,
                   "network": sc_network, "share": sc_share})


# ---------------------------------------------------------------- reel 019: peacekeeping
def _heli(d, x, y, sc_, col, rot):
    d.ellipse([x - 60 * sc_, y - 22 * sc_, x + 40 * sc_, y + 22 * sc_], fill=col)
    d.polygon([(x + 30 * sc_, y - 6 * sc_), (x + 120 * sc_, y - 14 * sc_), (x + 120 * sc_, y - 2 * sc_), (x + 30 * sc_, y + 8 * sc_)], fill=col)
    d.line([x + 118 * sc_, y - 30 * sc_, x + 118 * sc_, y + 6 * sc_], fill=col, width=max(2, int(4 * sc_)))
    d.line([x - 10 * sc_, y - 22 * sc_, x - 10 * sc_, y - 36 * sc_], fill=col, width=max(2, int(5 * sc_)))
    L = 110 * sc_ * abs(math.cos(rot)); d.line([x - 10 * sc_ - L, y - 38 * sc_, x - 10 * sc_ + L, y - 38 * sc_], fill=col, width=max(2, int(5 * sc_)))
    d.line([x - 60 * sc_, y + 30 * sc_, x + 30 * sc_, y + 30 * sc_], fill=col, width=max(2, int(4 * sc_)))

def sc_airlift(img, sc, t, D, tg, k):
    """Korea 1953: helicopters lift troops from ships at sea straight to the demilitarised zone (no road through the country)."""
    d = ImageDraw.Draw(img); top, bot = 300, 1060
    q = clamp(t / 0.5)
    rect_a(img, (60, top, W - 60, bot), (8, 18, 30), 0.85 * q, 26, T["accent"], 2)
    sea_x = 330
    d.rectangle([62, top + 2, sea_x, bot - 2], fill=(14, 40, 70, int(255 * q)))
    for j in range(9):
        y = top + 50 + j * 80; ph = math.sin(tg * 2 + j)
        d.arc([80 + 10 * ph, y, 300 + 10 * ph, y + 30], 200, 340, fill=(80, 140, 200, int(200 * q)), width=3)
    land = [(sea_x, top + 2), (W - 62, top + 2), (W - 62, bot - 2), (sea_x, bot - 2)]
    d.polygon(land, fill=(26, 40, 32, int(255 * q)))
    dz = W - 260
    for y in range(top + 20, bot - 20, 34): d.line([dz, y, dz, y + 18], fill=T["alert"] + (int(255 * q),), width=6)
    text_a(img, (dz, top + 40), "DMZ", F("anton", 52), T["alert"], q, "mm", shadow=6)
    text_a(img, (196, bot - 40), "SHIPS", F("mono", 28), (180, 210, 240), q, "mm")
    text_a(img, ((sea_x + dz) / 2, bot - 40), "NO PASSAGE BY ROAD", F("mono", 28), T["alert"], clamp((t - 1.2) / 0.5), "mm")
    for j in range(3):
        y = top + 170 + j * 220
        d.polygon([(110, y), (290, y), (270, y + 40), (130, y + 40)], fill=(150, 160, 170, int(255 * q)))
        d.rectangle([170, y - 34, 230, y], fill=(150, 160, 170, int(255 * q)))
    la = sc.get("lift_at", 1.0)
    for j in range(5):
        p = ((t - la) / 3.2 - j * 0.22) % 1.3
        if t < la or p > 1: continue
        x = 200 + (dz - 140 - 200) * ease_io(p); y = top + 170 + (j % 3) * 220 - 80 - 120 * math.sin(p * math.pi) + 60 * (j // 3)
        _heli(d, x, y, 0.75, (230, 236, 240, 255), tg * 30 + j)
    ca = sc.get("count_at", 2.0)
    if t > ca:
        rect_a(img, (dz - 150, top + 280, dz + 150, top + 560), (60, 20, 16), 0.9 * clamp((t - ca) / 0.4), 18, T["alert"], 3)
        text_a(img, (dz, top + 360), "POW", F("mono", 34), T["alert"], clamp((t - ca) / 0.4), "mm")
        for j in range(6):
            for i2 in range(5):
                xx, yy = dz - 110 + i2 * 55, top + 410 + j * 22
                d.ellipse([xx, yy, xx + 14, yy + 14], fill=(230, 210, 190, int(255 * clamp((t - ca - (j * 5 + i2) * 0.02) / 0.2))))
    caption(img, sc, t, D, 1130)
    chrome(img, tg)

def sc_medal(img, sc, t, D, tg, k):
    """A generic gallantry medal (not a reproduction of any real design) swinging in on its ribbon."""
    cx, cy = W / 2, 640; q = back(clamp((t - 0.2) / 0.8)); a = clamp((t - 0.2) / 0.4)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([cx - 360, cy - 360, cx + 360, cy + 300], fill=(255, 190, 90, int(120 * a)))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(90)))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.polygon([(cx - 90, 220), (cx + 90, 220), (cx + 70, 470), (cx - 70, 470)], fill=(150, 40, 60, 255))
    d.rectangle([cx - 20, 220, cx + 20, 470], fill=(110, 26, 44, 255))
    d.rectangle([cx - 100, 470, cx + 100, 500], fill=(190, 150, 70, 255))
    r = 190; my = 700
    d.ellipse([cx - r, my - r, cx + r, my + r], fill=(176, 120, 60, 255), outline=(240, 200, 120, 255), width=10)
    d.ellipse([cx - r + 34, my - r + 34, cx + r - 34, my + r - 34], outline=(120, 76, 34, 255), width=6)
    for j in range(8):
        an = j * math.pi / 4 + math.pi / 8
        d.line([cx + 40 * math.cos(an), my + 40 * math.sin(an), cx + 120 * math.cos(an), my + 120 * math.sin(an)], fill=(240, 200, 120, 255), width=10)
    d.ellipse([cx - 40, my - 40, cx + 40, my + 40], fill=(240, 200, 120, 255))
    sh = int(255 * (0.25 + 0.25 * math.sin(tg * 3)))
    d.chord([cx - r + 10, my - r + 10, cx + r - 10, my + r - 10], 200, 250, fill=(255, 240, 200, sh // 3))
    ang = 8 * math.sin(t * 2.2) * math.exp(-t * 0.6)
    lay = lay.rotate(ang, center=(cx, 220), resample=Image.BICUBIC)
    s = clamp(q, 0.3, 1.1)
    if s != 1:
        lay = lay.resize((int(W * s), int(H * s)), Image.LANCZOS)
        off = (int(cx - cx * s), int(220 - 220 * s)); tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0)); tmp.alpha_composite(lay.crop((max(0, -off[0]), 0, max(0, -off[0]) + W, H)) if off[0] < 0 else lay, (max(0, off[0]), max(0, off[1]))); lay = tmp
    paste_a(img, lay, (0, 0), a)
    caption(img, sc, t, D, 1130)
    chrome(img, tg)

R.SCENE_FN.update({"airlift": sc_airlift, "medal": sc_medal})


# ---------------------------------------------------------------- reel 020: who pays, who serves
def sc_split(img, sc, t, D, tg, k):
    """Two tall columns compared: each {flags, label, value, frac, color: accent|alert|gold, sub}. Bars grow, numbers count up."""
    chrome(img, tg)
    text_a(img, (W / 2, 300), sc.get("title", ""), fit_font("disp", 78, sc.get("title", ""), W - 120, "Black"), WHITE, clamp(t / 0.3), "mm", shadow=8)
    text_a(img, (W / 2, 384), typed(sc.get("kicker", ""), prog(t, 0.2, 0.8)), F("mono", 30), T["accent2"], 1, "mm")
    cols = sc["cols"]; ats = sc.get("col_at", [0.6 + i * 1.6 for i in range(len(cols))])
    base, top = 1500, 640; cw = 330
    for i, c in enumerate(cols):
        cx = W / 2 + (i - (len(cols) - 1) / 2) * 460; a = clamp((t - ats[i]) / 0.3); g = ease(clamp((t - ats[i] - 0.2) / 1.2))
        if a <= 0: continue
        col = {"accent": T["accent"], "alert": T["alert"], "gold": T["accent2"]}.get(c.get("color", "accent"), T["accent"])
        rect_a(img, (cx - cw / 2, top, cx + cw / 2, base), (10, 16, 26), 0.85 * a, 22, col, 2)
        h = (base - top - 40) * c["frac"] * g
        rect_a(img, (cx - cw / 2 + 20, base - 20 - max(8, h), cx + cw / 2 - 20, base - 20), col, 0.9 * a, 14)
        val = c["value"]
        try:
            num = float(val.replace(",", "").replace("%", "")); dec = len(val.replace("%", "").split(".")[1]) if "." in val else 0
            shown = f"{num * g:,.{dec}f}" + ("%" if val.endswith("%") else "")
        except ValueError:
            shown = val
        vy = max(top + 90, min(base - 90, base - 20 - h - 70))
        text_a(img, (cx, vy), shown, fit_font("anton", 110, val + "0", cw + 60), WHITE, a, "mm", shadow=10)
        text_a(img, (cx, base + 60), c["label"], fit_font("disp", 50, c["label"], cw + 100, "Black"), col, a, "mm")
        if c.get("sub"): text_a(img, (cx, base + 120), c["sub"], fit_font("inter", 34, c["sub"], cw + 110, "SemiBold"), MUTED, a, "mm")
        fl = c.get("flags", [])
        if fl:
            fw = min(96, int((cw + 80) / len(fl)) - 10); x0 = cx - (len(fl) * (fw + 10) - 10) / 2
            for j, code in enumerate(fl): paste_a(img, R.flag(code, fw), (x0 + j * (fw + 10), top - fw * 0.7 - 30), a)
    if sc.get("note"):
        na = sc.get("note_at", D * 0.75); text_a(img, (W / 2, 1730), sc["note"], fit_font("disp", 52, sc["note"], W - 120, "Black"), T["accent2"], clamp((t - na) / 0.4), "mm", shadow=8)

def sc_ledger(img, sc, t, D, tg, k):
    """Rows: [code, name, pay_label, pay_frac, men_label, men_frac] with two bars each: share of the bill vs soldiers sent."""
    chrome(img, tg)
    text_a(img, (80, 300), sc.get("title", ""), fit_font("disp", 76, sc.get("title", ""), W - 160, "Black"), WHITE, clamp(t / 0.3), shadow=6)
    text_a(img, (84, 392), typed(sc.get("kicker", ""), prog(t, 0.2, 0.8)), F("mono", 28), T["accent2"], 1)
    hx = [560, 840]; text_a(img, (hx[0], 470), "PAYS", F("mono", 30), T["accent2"], clamp(t / 0.4), "lm"); text_a(img, (hx[1], 470), "SOLDIERS", F("mono", 30), T["accent"], clamp(t / 0.4), "lm")
    rows = sc["rows"]; ats = sc.get("row_at", [0.5 + i * (D * 0.55) / len(rows) for i in range(len(rows))])
    for i, (code, name, pl, pf, ml, mf) in enumerate(rows):
        a = clamp((t - ats[i]) / 0.3); g = ease(clamp((t - ats[i] - 0.1) / 0.9)); y = 520 + i * 230
        if a <= 0: continue
        hl = i in sc.get("hl", [])
        rect_a(img, (50, y, W - 50, y + 200), (8, 13, 22), 0.85 * a, 20, T["alert"] if hl else None, 3)
        paste_a(img, R.flag(code, 110), (80, y + 30), a)
        text_a(img, (80, y + 160), name, fit_font("inter", 34, name, 400, "SemiBold"), WHITE, a, "lm")
        text_a(img, (hx[0], y + 60), pl, F("anton", 64), T["accent2"], a, "lm")
        rect_a(img, (hx[0], y + 120, hx[0] + max(6, 240 * pf * g), y + 150), T["accent2"], a, 6)
        text_a(img, (hx[1], y + 60), ml, F("anton", 64), WHITE, a, "lm")
        rect_a(img, (hx[1], y + 120, hx[1] + max(6, 180 * mf * g), y + 150), T["accent"], a, 6)
    if sc.get("note"):
        na = sc.get("note_at", D * 0.8); text_a(img, (W / 2, 520 + len(rows) * 230 + 40), sc["note"], fit_font("disp", 50, sc["note"], W - 120, "Black"), T["alert"], clamp((t - na) / 0.4), "mm", shadow=8)

R.SCENE_FN.update({"split": sc_split, "ledger": sc_ledger})


# ---------------------------------------------------------------- reel 020: Cipla (light "pharma" theme)
INKD = (22, 30, 40); TEAL = (0, 140, 130); SAFF = (240, 120, 20); GRN = (19, 136, 8); REDC = (214, 48, 60)

def card(img, box, a=1.0, r=28, fill=(255, 255, 255), outline=None):
    """White card with a soft drop shadow (light themes)."""
    if a <= 0: return
    x0, y0, x1, y1 = [int(v) for v in box]
    sh = Image.new("RGBA", (x1 - x0 + 80, y1 - y0 + 80), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([40, 52, x1 - x0 + 40, y1 - y0 + 52], r, fill=(30, 50, 60, int(60 * a)))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)), (x0 - 40, y0 - 40))
    rect_a(img, (x0, y0, x1, y1), fill, a, r, outline or (220, 228, 230), 2)

def pill(w, h, c1, c2, band=None, label=None):
    """Horizontal capsule image."""
    K = 2; im = Image.new("RGBA", (w * K, h * K), (0, 0, 0, 0)); d = ImageDraw.Draw(im); r = h * K // 2
    d.rounded_rectangle([0, 0, w * K - 1, h * K - 1], r, fill=c1 + (255,))
    half = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(half).rounded_rectangle([0, 0, w * K - 1, h * K - 1], r, fill=c2 + (255,))
    mask = Image.new("L", im.size, 0); ImageDraw.Draw(mask).rectangle([w * K // 2, 0, w * K, h * K], fill=255)
    im.paste(half, (0, 0), mask)
    if band: d.rectangle([w * K // 2 - 8 * K, 0, w * K // 2 + 8 * K, h * K], fill=band + (255,))
    d.rounded_rectangle([0, 0, w * K - 1, h * K - 1], r, outline=(255, 255, 255, 200), width=3 * K)
    d.rounded_rectangle([r * 0.6, h * K * 0.16, w * K * 0.42, h * K * 0.3], h * K // 10, fill=(255, 255, 255, 120))
    im = im.resize((w, h), Image.LANCZOS)
    if label:
        d = ImageDraw.Draw(im); f = fit_font("disp", int(h * 0.36), label, w - h, "Black")
        d.text((w / 2, h / 2), label, font=f, fill=(255, 255, 255, 255), anchor="mm")
    return im

def sc_l_hook(img, sc, t, D, tg, k):
    """David vs Goliath: a small India-coloured capsule faces five 'Big Pharma' towers, then knocks them off balance."""
    base = 1520; hit = sc.get("hit_at", 2.4)
    shake = 0
    if t > hit: shake = 14 * math.exp(-(t - hit) * 2.5) * math.sin((t - hit) * 40)
    lean = clamp((t - hit) / 1.2) * 4
    for i in range(5):
        x = 470 + i * 112; h = 560 + (i * 137) % 220; a = clamp((t - 0.1 * i) / 0.4)
        lay = Image.new("RGBA", (130, h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.rectangle([5, 10, 120, h + 19], fill=(84, 98, 118, 255)); d.rectangle([5, 10, 120, 40], fill=(62, 74, 92, 255))
        for r_ in range(int((h - 60) / 54)):
            for c in range(3): d.rectangle([20 + c * 34, 60 + r_ * 54, 40 + c * 34, 90 + r_ * 54], fill=(200, 216, 232, 255) if (r_ + c + i) % 4 else (255, 214, 120, 255))
        lay = lay.rotate(-lean * (1 + i * 0.2), center=(65, h + 20), resample=Image.BICUBIC, expand=False)
        paste_a(img, lay, (x + shake, base - h - 20), a)
    rect_a(img, (470, base - 4, 1040, base + 8), (62, 74, 92), clamp(t / 0.4))
    ba = clamp((t - 0.6) / 0.4)
    rect_a(img, (520, 1110, 1000, 1190), (40, 50, 64), ba * 0.95, 16)
    text_a(img, (760, 1150), "BIG PHARMA", F("anton", 64), (255, 255, 255), ba, "mm")
    p = pill(300, 120, SAFF, GRN, band=(255, 255, 255))
    if t < hit - 0.9:
        x, y, ang = 250, base - 70 + 6 * math.sin(tg * 3), 0
    else:
        q = clamp((t - (hit - 0.9)) / 0.9); x = 250 + 200 * ease(q); y = base - 70 - 260 * math.sin(q * math.pi) * (1 - q * 0.3); ang = -360 * ease(q)
        if t > hit: x, y, ang = 450 - 30 * clamp((t - hit) / 0.5), base - 70, 0
    pr = p.rotate(ang, expand=True, resample=Image.BICUBIC)
    paste_a(img, pr, (x - pr.width / 2, y - pr.height / 2), clamp(t / 0.3))
    text_a(img, (250, base + 70), "1 INDIAN COMPANY", F("disp", 34, "Black"), SAFF, clamp((t - 0.8) / 0.4), "mm")
    for i, (s, col) in enumerate(sc.get("title", [])):
        ta = sc.get("title_at", 0.6) + i * 0.35; q = back(clamp((t - ta) / 0.45))
        text_a(img, (80, 330 + i * 140), s, F("anton", int(130 * clamp(q, 0.3, 1.1))), T.get(col, INKD) if col != "WHITE" else INKD, clamp((t - ta) / 0.25), shadow=6)
    chrome(img, tg)

def sc_l_pricetag(img, sc, t, D, tg, k):
    """A swinging paper price tag with the year-2000 price."""
    q = back(clamp((t - 0.2) / 0.7)); a = clamp((t - 0.2) / 0.3)
    ang = 10 * math.sin(t * 2.4) * math.exp(-t * 0.5)
    w, h = 760, 430; lay = Image.new("RGBA", (w + 200, h + 300), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    ox, oy = 100, 160
    d.line([ox + w / 2 - 260, 0, ox + 70, oy + h / 2], fill=(150, 120, 80, 255), width=6)
    d.polygon([(ox, oy + h / 2), (ox + 120, oy), (ox + w, oy), (ox + w, oy + h), (ox + 120, oy + h)], fill=(255, 236, 200, 255), outline=(200, 160, 100, 255))
    d.ellipse([ox + 50, oy + h / 2 - 22, ox + 94, oy + h / 2 + 22], fill=(246, 248, 245, 255), outline=(200, 160, 100, 255), width=4)
    f = fit_font("anton", 170, sc["price"], w - 220); d.text((ox + 160, oy + 160), sc["price"], font=f, fill=REDC + (255,), anchor="lm")
    d.text((ox + 165, oy + 320), sc.get("per", "PER PATIENT · PER YEAR"), font=F("disp", 40, "Black"), fill=INKD + (255,), anchor="lm")
    lay = lay.rotate(ang, center=(ox + w / 2 - 260, 0), resample=Image.BICUBIC)
    s = clamp(q, 0.4, 1.1); lay = lay.resize((int(lay.width * s), int(lay.height * s)), Image.LANCZOS)
    paste_a(img, lay, (W / 2 - lay.width / 2 + 100 * s, 430), a)
    caption(img, sc, t, D, 1150)
    chrome(img, tg)

def sc_l_pills(img, sc, t, D, tg, k):
    """Three separate medicines slide together into one pill."""
    names = sc.get("names", ["STAVUDINE", "LAMIVUDINE", "NEVIRAPINE"]); cols = [((90, 140, 220), (60, 110, 200)), ((240, 170, 40), (226, 140, 20)), ((120, 190, 120), (80, 160, 90))]
    ma = sc.get("merge_at", 2.5); m = ease(clamp((t - ma) / 0.9))
    for i in range(3):
        a = clamp((t - 0.3 - i * 0.35) / 0.3)
        y0 = 520 + i * 230; y = y0 + (750 - y0) * m
        x = W / 2 + (i - 1) * 40 * (1 - m)
        p = pill(420, 150, *cols[i], label=names[i])
        paste_a(img, p, (x - 210, y - 75), a * (1 - clamp((t - ma - 0.7) / 0.3)))
    if t > ma + 0.6:
        q = back(clamp((t - ma - 0.6) / 0.6)); s = clamp(q, 0.3, 1.15)
        p = pill(int(560 * s), int(200 * s), TEAL, (0, 110, 104), label="3-IN-1")
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(glow).ellipse([W / 2 - 380, 520, W / 2 + 380, 980], fill=TEAL + (int(70 * clamp(q, 0, 1)),))
        img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(60)))
        paste_a(img, p, (W / 2 - p.width / 2, 750 - p.height / 2), 1)
    caption(img, sc, t, D, 1150)
    chrome(img, tg)

def sc_l_slash(img, sc, t, D, tg, k):
    """Old price struck through, new price counts down, then the discount stamp and the 'less than $1 a day' chip."""
    card(img, (90, 330, W - 90, 1060), clamp(t / 0.3))
    text_a(img, (W / 2, 400), sc.get("kicker", ""), F("mono", 32), TEAL, clamp(t / 0.3), "mm")
    text_a(img, (W / 2, 520), sc.get("old_label", "USA PRICE"), F("disp", 36, "Bold"), R.MUTED, clamp(t / 0.3), "mm")
    text_a(img, (W / 2, 620), sc["old"], F("anton", 130), (150, 158, 166), clamp(t / 0.3), "mm")
    sa = sc.get("slash_at", 1.0); q = ease(clamp((t - sa) / 0.4))
    if q > 0:
        d = ImageDraw.Draw(img); d.line([W / 2 - 300, 650, W / 2 - 300 + 600 * q, 590], fill=REDC + (255,), width=14)
    na = sc.get("new_at", 1.6); g = ease(clamp((t - na) / 1.2))
    if t > na:
        o, n = float(sc["old"].replace("$", "").replace(",", "")), float(sc["new"].replace("$", "").replace(",", ""))
        v = o + (n - o) * g
        text_a(img, (W / 2, 760), sc.get("new_label", "CIPLA OFFER"), F("disp", 36, "Bold"), TEAL, clamp((t - na) / 0.3), "mm")
        text_a(img, (W / 2, 890), f"${v:,.0f}", F("anton", 190), TEAL, clamp((t - na) / 0.3), "mm", shadow=6)
    st = sc.get("stamp_at", 3.2)
    if t > st:
        q = back(clamp((t - st) / 0.4)); s = clamp(q, 0.3, 1.2)
        lay = Image.new("RGBA", (520, 190), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle([6, 6, 514, 184], 26, outline=REDC + (255,), width=10); ld.text((260, 95), sc.get("stamp", "−96.6%"), font=F("anton", 110), fill=REDC + (255,), anchor="mm")
        lay = lay.rotate(-8, expand=True, resample=Image.BICUBIC); lay = lay.resize((int(lay.width * s), int(lay.height * s)), Image.LANCZOS)
        paste_a(img, lay, (W - 120 - lay.width, 1000 - lay.height / 2), clamp((t - st) / 0.15))
    ca = sc.get("chip_at", 4.2)
    if t > ca:
        q = clamp((t - ca) / 0.4); s = sc.get("chip", "LESS THAN $1 A DAY"); f = F("disp", 56, "Black")
        w = ImageDraw.Draw(img).textlength(s, font=f)
        rect_a(img, (W / 2 - w / 2 - 40, 1150, W / 2 + w / 2 + 40, 1250), SAFF, q, 50)
        text_a(img, (W / 2, 1200), s, f, (255, 255, 255), q, "mm")
    for i, ln in enumerate(sc.get("lines", [])):
        text_a(img, (W / 2, 1340 + i * 70), typed(ln, prog(t, 1.0 + i * 0.6, 0.7)), fit_font("disp", 50, ln, W - 140, "Bold"), INKD, 1, "mm")
    chrome(img, tg)

def lock(d, x, y, s, closed, col):
    d.rounded_rectangle([x - 50 * s, y, x + 50 * s, y + 80 * s], 12 * s, fill=col + (255,))
    if closed: d.arc([x - 34 * s, y - 60 * s, x + 34 * s, y + 20 * s], 180, 360, fill=col + (255,), width=int(14 * s))
    else: d.arc([x - 34 * s + 40 * s, y - 70 * s, x + 34 * s + 40 * s, y + 10 * s], 180, 330, fill=col + (255,), width=int(14 * s))
    d.ellipse([x - 10 * s, y + 25 * s, x + 10 * s, y + 45 * s], fill=(255, 255, 255, 255))

def sc_l_law(img, sc, t, D, tg, k):
    """India's patent law: the medicine itself could not be patented, only the method. Then the 'PIRATE?' stamp."""
    for i, (title, sub, closed, col) in enumerate(sc["cards"]):
        col = tuple(col)
        ca = sc.get("card_at", [0.4, 1.8])[i]; a = clamp((t - ca) / 0.4); y0 = 340 + i * 420
        if a <= 0: continue
        card(img, (90, y0, W - 90, y0 + 370), a)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); lock(ImageDraw.Draw(lay), 220, y0 + 130, 1.2, closed, col); img.alpha_composite(lay)
        text_a(img, (340, y0 + 110), title, fit_font("disp", 56, title, W - 480, "Black"), INKD, a)
        for j, ln in enumerate(sub): text_a(img, (342, y0 + 200 + j * 56), ln, fit_font("inter", 40, ln, W - 480, "SemiBold"), col, a)
    pa = sc.get("pirate_at", D * 0.65)
    if t > pa:
        q = back(clamp((t - pa) / 0.4)); s = clamp(q, 0.3, 1.2)
        lay = Image.new("RGBA", (640, 200), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle([6, 6, 634, 194], 26, outline=REDC + (255,), width=10); ld.text((320, 100), sc.get("stamp", "“PIRATE?”"), font=F("anton", 110), fill=REDC + (255,), anchor="mm")
        lay = lay.rotate(6, expand=True, resample=Image.BICUBIC); lay = lay.resize((int(lay.width * s), int(lay.height * s)), Image.LANCZOS)
        paste_a(img, lay, (W / 2 - lay.width / 2, 1250 - lay.height / 2), clamp((t - pa) / 0.15))
        if sc.get("stamp_sub"): text_a(img, (W / 2, 1420), sc["stamp_sub"], fit_font("inter", 38, sc["stamp_sub"], W - 160, "SemiBold"), R.MUTED, clamp((t - pa - 0.4) / 0.4), "mm")
    chrome(img, tg)

def sc_l_court(img, sc, t, D, tg, k):
    """39 company blocks line up against one country; on drop_at they topple and fade."""
    text_a(img, (W / 2, 340), sc.get("title", ""), fit_font("disp", 62, sc.get("title", ""), W - 140, "Black"), INKD, clamp(t / 0.3), "mm")
    text_a(img, (W / 2, 420), typed(sc.get("kicker", ""), prog(t, 0.2, 0.7)), F("mono", 30), TEAL, 1, "mm")
    da = sc.get("drop_at", D * 0.6); n = sc.get("n", 39)
    for i in range(n):
        r_, c = divmod(i, 8); x = 150 + c * 105; y = 520 + r_ * 110
        a = clamp((t - 0.4 - i * 0.03) / 0.2)
        if t > da:
            q = clamp((t - da - (i % 8) * 0.05) / 0.6); y += 500 * q * q; a *= 1 - q
        if a <= 0: continue
        rect_a(img, (x, y, x + 86, y + 90), (84, 98, 118), a, 10)
        for wy in range(2):
            for wx in range(3): rect_a(img, (x + 12 + wx * 24, y + 16 + wy * 30, x + 26 + wx * 24, y + 36 + wy * 30), (200, 216, 232), a, 2)
    if t > 0.8:
        a = clamp((t - 0.8) / 0.4); card(img, (300, 1100, 780, 1240), a)
        text_a(img, (540, 1170), sc.get("vs", "vs SOUTH AFRICA"), F("disp", 48, "Black"), INKD, a, "mm")
    if t > da + 0.5:
        q = back(clamp((t - da - 0.5) / 0.5)); a = clamp((t - da - 0.5) / 0.3)
        text_a(img, (W / 2, 1350), sc.get("result", "CASE DROPPED"), F("anton", int(130 * clamp(q, 0.3, 1.1))), TEAL, a, "mm", shadow=6)
        text_a(img, (W / 2, 1460), sc.get("date", ""), F("mono", 36), R.MUTED, a, "mm")
    chrome(img, tg)

def sc_l_chart(img, sc, t, D, tg, k):
    """Price per patient per year falling: bars with labels."""
    text_a(img, (W / 2, 340), sc.get("title", ""), fit_font("disp", 60, sc.get("title", ""), W - 140, "Black"), INKD, clamp(t / 0.3), "mm")
    text_a(img, (W / 2, 420), typed(sc.get("kicker", ""), prog(t, 0.2, 0.7)), F("mono", 30), TEAL, 1, "mm")
    card(img, (90, 480, W - 90, 1420), clamp(t / 0.3))
    bars = sc["bars"]; mx = max(b[1] for b in bars); ats = sc.get("bar_at", [0.6 + i * 1.2 for i in range(len(bars))])
    base = 1280; top = 600; bw = 200
    for i, (lab, v, vs) in enumerate(bars):
        x = 200 + i * 270; g = ease(clamp((t - ats[i]) / 0.9)); a = clamp((t - ats[i]) / 0.3)
        if a <= 0: continue
        h = max(10, (base - top) * v / mx * g)
        rect_a(img, (x, base - h, x + bw, base), REDC if i == 0 else TEAL, a, 14)
        text_a(img, (x + bw / 2, base - h - 50), vs, F("anton", 70), REDC if i == 0 else TEAL, a, "mm")
        text_a(img, (x + bw / 2, base + 60), lab, F("disp", 46, "Black"), INKD, a, "mm")
    if sc.get("note"):
        na = sc.get("note_at", D * 0.75); text_a(img, (W / 2, 1520), sc["note"], fit_font("disp", 52, sc["note"], W - 140, "Black"), SAFF, clamp((t - na) / 0.4), "mm")
    chrome(img, tg)

def sc_l_donut(img, sc, t, D, tg, k):
    """Donut share with the India flag at the centre."""
    cx, cy, r = W / 2, 760, 330; g = ease(clamp((t - 0.6) / 1.6)); a = clamp(t / 0.3)
    card(img, (90, 330, W - 90, 1190), a)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(226, 232, 236, int(255 * a)))
    d.pieslice([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * sc["share"] * g, fill=SAFF + (int(255 * a),))
    d.ellipse([cx - r * 0.62, cy - r * 0.62, cx + r * 0.62, cy + r * 0.62], fill=(255, 255, 255, int(255 * a)))
    img.alpha_composite(lay)
    paste_a(img, R.flag("IN", 150), (cx - 75, cy - 150), a)
    text_a(img, (cx, cy + 70), f"{round(sc['share'] * 100 * g)}%", F("anton", 120), SAFF, a, "mm")
    caption(img, sc, t, D, 1290)
    chrome(img, tg)

def person_icon(d, x, y, s, col):
    d.ellipse([x - 14 * s, y, x + 14 * s, y + 28 * s], fill=col + (255,))
    d.rounded_rectangle([x - 22 * s, y + 32 * s, x + 22 * s, y + 80 * s], 14 * s, fill=col + (255,))

def sc_l_people(img, sc, t, D, tg, k):
    """People on treatment: a grid of figures that light up from the old number to the new one, with a counter."""
    a = clamp(t / 0.3); card(img, (90, 330, W - 90, 1130), a)
    n0, n1 = sc["from"], sc["to"]; g = ease(clamp((t - sc.get("grow_at", 1.0)) / 2.2)); v = n0 + (n1 - n0) * g
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    total = int(round(n1)); lit = v
    for i in range(total + 3):
        r_, c = divmod(i, 7); x = 210 + c * 110; y = 380 + r_ * 140
        if y > 1050: break
        col = TEAL if i < int(lit) else (214, 222, 226)
        if i < int(round(n0)): col = (0, 110, 104)
        person_icon(d, x, y, 1.0, col)
    paste_a(img, lay, (0, 0), a)
    text_a(img, (W / 2, 1230), f"{v:.1f} MILLION", F("anton", 140), TEAL, clamp((t - 0.6) / 0.3), "mm", shadow=6)
    for i, ln in enumerate(sc.get("lines", [])):
        text_a(img, (W / 2, 1360 + i * 66), typed(ln, prog(t, 1.2 + i * 0.6, 0.7)), fit_font("disp", 48, ln, W - 140, "Bold"), INKD, 1, "mm")
    chrome(img, tg)

R.SCENE_FN.update({"l_hook": sc_l_hook, "l_pricetag": sc_l_pricetag, "l_pills": sc_l_pills, "l_slash": sc_l_slash, "l_law": sc_l_law,
                   "l_court": sc_l_court, "l_chart": sc_l_chart, "l_donut": sc_l_donut, "l_people": sc_l_people})


# ---------------------------------------------------------------- reel 022: weapon material left over (punch format)
def atom(img, cx, cy, r, tg, a, col):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for j in range(3):
        e = Image.new("RGBA", (int(r * 2.4), int(r * 2.4)), (0, 0, 0, 0)); ImageDraw.Draw(e).ellipse([r * 0.2, r * 0.85, r * 2.2, r * 1.55], outline=col + (230,), width=max(4, r // 30))
        e = e.rotate(j * 60 + tg * 12, resample=Image.BICUBIC); lay.alpha_composite(e, (int(cx - r * 1.2), int(cy - r * 1.2)))
        ang = tg * (2.2 + j * 0.7) + j * 2.1; ex, ey = r * math.cos(ang), r * 0.35 * math.sin(ang)
        rot = math.radians(-(j * 60 + tg * 12)); px, py = cx + ex * math.cos(rot) - ey * math.sin(rot), cy + ex * math.sin(rot) + ey * math.cos(rot)
        d.ellipse([px - r * 0.07, py - r * 0.07, px + r * 0.07, py + r * 0.07], fill=(255, 255, 255, 255))
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse([cx - r * 0.5, cy - r * 0.5, cx + r * 0.5, cy + r * 0.5], fill=col + (200,))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(r // 4))); d.ellipse([cx - r * 0.18, cy - r * 0.18, cx + r * 0.18, cy + r * 0.18], fill=col + (255,))
    paste_a(img, lay, (0, 0), a)

def sc_n_hook(img, sc, t, D, tg, k):
    """Frame one is already loud: crossed-out bombs number, then the 'material left' reveal."""
    atom(img, W / 2, 1060, 230, tg, 1.0, T["accent"])
    text_a(img, (W / 2, 330), sc.get("top", ""), fit_font("anton", 150, sc.get("top", ""), W - 120), WHITE, 1, "mm", shadow=10)
    q = ease(clamp((t - 0.25) / 0.35)); d = ImageDraw.Draw(img)
    if q > 0: d.line([150, 370, 150 + (W - 300) * q, 290], fill=T["alert"] + (255,), width=18)
    text_a(img, (W / 2, 450), sc.get("top_sub", ""), F("hindi", 64), MUTED, 1, "mm", shadow=6)
    ra = sc.get("reveal_at", 2.0)
    if t > ra:
        q = back(clamp((t - ra) / 0.5))
        text_a(img, (W / 2, 620), sc.get("big", ""), fit_font("anton", int(190 * clamp(q, 0.3, 1.1)), sc.get("big", ""), W - 100), T["accent"], clamp((t - ra) / 0.2), "mm", shadow=12)
        text_a(img, (W / 2, 760), sc.get("big_sub", ""), F("hindi", 66), WHITE, clamp((t - ra - 0.2) / 0.3), "mm", shadow=8)
    chrome(img, tg)

def cylinder(img, x, y0, y1, w, frac, col, a, label, val):
    rect_a(img, (x - w / 2, y0, x + w / 2, y1), (20, 24, 26), 0.85 * a, 30, col, 3)
    h = (y1 - y0 - 16) * frac
    rect_a(img, (x - w / 2 + 8, y1 - 8 - h, x + w / 2 - 8, y1 - 8), col, 0.85 * a, 24)
    text_a(img, (x, y1 - 8 - h - 60), val, F("anton", 84), WHITE, a, "mm", shadow=8)
    text_a(img, (x, y1 + 56), label, fit_font("disp", 44, label, w + 140, "Black"), col, a, "mm")

def sc_n_stock(img, sc, t, D, tg, k):
    text_a(img, (W / 2, 330), sc.get("kicker", ""), F("mono", 34), T["accent2"], clamp(t / 0.2), "mm")
    g = ease(clamp((t - 0.2) / 1.4)); tot = sc["total"]
    text_a(img, (W / 2, 460), f"{tot * g:,.0f} TONNES", F("anton", 140), WHITE, 1, "mm", shadow=10)
    for i, (lab, v, col) in enumerate(sc["parts"]):
        a = clamp((t - 0.6 - i * 0.4) / 0.3); cylinder(img, W / 2 + (i - 0.5) * 420, 640, 1210, 300, v / tot * g, T[col], a, lab, f"{v * g:,.0f} t")
    chrome(img, tg)

def bomb_icon(d, x, y, s, col):
    d.ellipse([x - 22 * s, y - 22 * s, x + 22 * s, y + 22 * s], fill=col + (255,)); d.rectangle([x - 6 * s, y - 34 * s, x + 6 * s, y - 20 * s], fill=col + (255,))
    d.line([x, y - 34 * s, x + 10 * s, y - 44 * s], fill=(255, 200, 80, 255), width=max(2, int(3 * s)))

def sc_n_math(img, sc, t, D, tg, k):
    """8 kg = 1 bomb, then a field of bombs and a counter racing past today's arsenal."""
    a = clamp(t / 0.2)
    rect_a(img, (90, 290, W - 90, 520), (16, 20, 22), 0.85 * a, 26, T["accent"], 2)
    text_a(img, (W / 2, 360), sc.get("eq1", ""), F("anton", 80), WHITE, a, "mm"); text_a(img, (W / 2, 460), sc.get("eq2", ""), F("anton", 60), MUTED, a, "mm")
    ca = sc.get("count_at", 2.5); g = ease(clamp((t - ca) / 2.0))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    n = int(100 * g)
    for i in range(100):
        r_, c = divmod(i, 10); col = T["alert"] if i < 10 else T["accent"]
        if i < n: bomb_icon(d, 150 + c * 87, 610 + r_ * 56, 0.85, col)
    paste_a(img, lay, (0, 0), 1)
    if t > ca:
        v = sc["count"] * g
        text_a(img, (W / 2, 1280), f"≈ {v:,.0f}", F("anton", 120), T["accent"], clamp((t - ca) / 0.3), "mm", shadow=10)
    if t > ca + 2.3:
        text_a(img, (W / 2, 1180), sc.get("vs", ""), F("disp", 40, "Black"), T["alert"], clamp((t - ca - 2.3) / 0.4), "mm")
    chrome(img, tg)

def sc_n_flagstat(img, sc, t, D, tg, k):
    a = clamp(t / 0.2); q = back(clamp(t / 0.5))
    paste_a(img, R.flag(sc["code"], int(300 * clamp(q, 0.3, 1.1))), (W / 2 - 150 * clamp(q, 0.3, 1.1), 330), a)
    text_a(img, (W / 2, 640), sc.get("big", ""), fit_font("anton", 170, sc.get("big", ""), W - 120), WHITE, a, "mm", shadow=10)
    text_a(img, (W / 2, 770), sc.get("sub", ""), fit_font("disp", 50, sc.get("sub", ""), W - 140, "Black"), MUTED, clamp((t - 0.4) / 0.3), "mm")
    ra = sc.get("reveal_at", 1.8)
    if t > ra:
        q2 = back(clamp((t - ra) / 0.5)); s = sc.get("reveal", "")
        rect_a(img, (110, 880, W - 110, 1180), (16, 20, 22), 0.9 * clamp((t - ra) / 0.2), 30, T["alert"], 4)
        text_a(img, (W / 2, 990), s, fit_font("anton", int(130 * clamp(q2, 0.3, 1.1)), s, W - 280), T["alert"], clamp((t - ra) / 0.2), "mm", shadow=8)
        text_a(img, (W / 2, 1110), sc.get("reveal_sub", ""), fit_font("disp", 44, sc.get("reveal_sub", ""), W - 280, "Black"), WHITE, clamp((t - ra - 0.3) / 0.3), "mm")
    chrome(img, tg)

R.SCENE_FN.update({"n_hook": sc_n_hook, "n_stock": sc_n_stock, "n_math": sc_n_math, "n_flagstat": sc_n_flagstat})


# ---------------------------------------------------------------- reel 024: America restarts bomb-core (pit) production
_sph = {}
def pit_sphere(r):
    """Metallic plutonium ball (cached RGBA, 2r x 2r) with a warm rim light."""
    if r in _sph: return _sph[r]
    yy, xx = np.mgrid[-r:r, -r:r].astype(np.float32) / r
    rr = np.sqrt(xx ** 2 + yy ** 2); m = rr <= 1
    z = np.sqrt(np.clip(1 - rr ** 2, 0, 1))
    L = np.clip(-0.45 * xx - 0.55 * yy + 0.7 * z, 0, 1)
    spec = np.clip(L, 0, 1) ** 18
    base = np.stack([150 + 70 * L, 152 + 64 * L, 150 + 52 * L], -1)
    rim = np.clip((rr - 0.72) / 0.28, 0, 1)[..., None] ** 2 * np.array([255, 120, 40])
    col = np.clip(base * (0.35 + 0.65 * L[..., None]) + rim * 0.9 + spec[..., None] * 255, 0, 255)
    a = (np.clip((1 - rr) * r / 1.5, 0, 1) * 255)
    im = Image.fromarray(np.dstack([col, a]).astype(np.uint8), "RGBA"); _sph[r] = im; return im

def draw_pit(img, cx, cy, r, tg, a=1.0, heat=1.0, beat=True):
    p = 0.5 + 0.5 * math.sin(tg * 7.0) if beat else 0.5
    p = max(0.0, math.sin(tg * 6.3)) ** 6 if beat else 0.3
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gr = r * (1.55 + 0.25 * p)
    ImageDraw.Draw(g).ellipse([cx - gr, cy - gr, cx + gr, cy + gr], fill=(255, 90, 30, int((90 + 110 * p) * heat * a)))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(r * 0.45)))
    s = pit_sphere(int(r)); paste_a(img, s, (cx - s.width / 2, cy - s.height / 2), a)

def alarm(img, tg, s=1.0):
    """Red siren wash pulsing in from the screen edges."""
    if s <= 0: return
    p = (0.5 + 0.5 * math.sin(tg * 2 * math.pi * 1.1)) ** 2 * s
    if p < 0.02: return
    global _alarm
    try: _alarm
    except NameError:
        yy, xx = np.mgrid[0:H, 0:W]; e = np.clip(np.maximum(np.abs(xx - W / 2) / (W / 2), np.abs(yy - H / 2) / (H / 2)) - 0.55, 0, 1) / 0.45
        _alarm = (e ** 1.6 * 255).astype(np.uint8)
    lay = Image.new("RGBA", (W, H), (255, 30, 30, 0)); lay.putalpha(Image.fromarray((_alarm * (0.75 * p)).astype(np.uint8)))
    img.alpha_composite(lay)

def stamp_img(lab, size=84, col=(220, 40, 40), rot=-10):
    f = F("anton", size); tw = ImageDraw.Draw(Image.new("L", (1, 1))).textlength(lab, font=f)
    st = Image.new("RGBA", (int(tw) + 70, int(size * 1.6)), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
    sd.rounded_rectangle([6, 6, st.width - 6, st.height - 6], 12, outline=col + (240,), width=8)
    sd.text((st.width / 2, st.height / 2), lab, font=f, fill=col + (240,), anchor="mm")
    return st.rotate(rot, expand=True, resample=Image.BICUBIC)

def slam(img, st, cx, cy, t0, t, max_w=None):
    sp = clamp((t - t0) / 0.18)
    if sp <= 0: return
    s = (2.0 - 1.0 * ease(sp)) * (min(1, max_w / st.width) if max_w else 1)
    im = st.resize((int(st.width * s), int(st.height * s)), Image.LANCZOS)
    sh = 10 * max(0, 1 - (t - t0) / 0.3)
    paste_a(img, im, (cx - im.width / 2 + sh * math.sin(t * 90), cy - im.height / 2), clamp(sp * 1.5))

def sc_p_hook(img, sc, t, D, tg, k):
    """Frame one is already loud: red headline + beating plutonium heart under a siren; then 180/YEAR slams, then a NO LIMITS stamp."""
    beat = max(0.0, math.sin(tg * 6.3)) ** 6
    alarm(img, tg, 0.85)
    sh = 7 * beat
    text_a(img, (W / 2 + sh, 320), sc.get("top", ""), fit_font("anton", 112, sc.get("top", ""), W - 130), WHITE, 1, "mm", shadow=10)
    text_a(img, (W / 2 - sh, 450), sc.get("top2", ""), fit_font("anton", 132, sc.get("top2", ""), W - 90), T["alert"], 1, "mm", shadow=12)
    ra, sa = sc.get("reveal_at", 3.0), sc.get("stamp_at", 6.0)
    py = 850 - 140 * ease(clamp((t - ra) / 0.5))
    draw_pit(img, W / 2, py, int(200 + 12 * beat - 60 * ease(clamp((t - ra) / 0.5))), tg)
    if t > ra:
        g = back(clamp((t - ra) / 0.45)); s_ = clamp(g, 0.3, 1.12)
        text_a(img, (W / 2, 1010), sc.get("num", ""), F("anton", int(250 * s_)), T["accent"], clamp((t - ra) / 0.12), "mm", shadow=14)
        text_a(img, (W / 2, 1165), sc.get("num_sub", ""), F("disp", 50, "Black"), WHITE, clamp((t - ra - 0.2) / 0.2), "mm", shadow=6)
        if t < ra + 0.15: img.alpha_composite(Image.new("RGBA", (W, H), (255, 240, 200, int(140 * (1 - (t - ra) / 0.15)))))
    if t > sa: slam(img, stamp_img(sc.get("stamp", ""), 86, rot=-9), W / 2, 1310, sa, t, max_w=W - 100)
    chrome(img, tg)

def sc_p_pit(img, sc, t, D, tg, k):
    """Warhead cross-section: explosive lenses around the pit; at squeeze_at they crush inward -> flash."""
    cx, cy = W / 2, 880; sq = sc.get("squeeze_at", 5.0); u = clamp((t - sq) / 0.35)
    a = clamp(t / 0.3)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    rc = 400
    d.ellipse([cx - rc, cy - rc, cx + rc, cy + rc], fill=(26, 30, 28, 235), outline=(120, 130, 120, 255), width=6)
    rin, rout = 205 - 80 * ease(u), 380 - 150 * ease(u); n = 24
    for i in range(n):
        a0 = 2 * math.pi * i / n + 0.03; a1 = 2 * math.pi * (i + 1) / n - 0.03
        pts = [(cx + rin * math.cos(a0), cy + rin * math.sin(a0)), (cx + rout * math.cos(a0), cy + rout * math.sin(a0)),
               (cx + rout * math.cos(a1), cy + rout * math.sin(a1)), (cx + rin * math.cos(a1), cy + rin * math.sin(a1))]
        c = (255, 140, 40) if i % 2 == 0 else (220, 100, 30)
        d.polygon(pts, fill=c + (255,))
        if t > sq - 0.6 and t < sq:   # detonators flash around the rim just before the squeeze
            if int(tg * 30 + i) % 3 == 0:
                px, py = cx + (rout + 14) * math.cos((a0 + a1) / 2), cy + (rout + 14) * math.sin((a0 + a1) / 2)
                d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=(255, 255, 200, 255))
    paste_a(img, lay, (0, 0), a)
    draw_pit(img, cx, cy, int(170 - 70 * ease(u)), tg, a, heat=1 + 2 * u)
    # labels
    la = clamp((t - 0.5) / 0.4) * (1 - clamp((t - sq) / 0.3))
    text_a(img, (W / 2, 330), sc.get("label", ""), F("anton", 110), T["accent"], la, "mm", shadow=10)
    text_a(img, (W / 2, 425), sc.get("label_sub", ""), F("disp", 42, "Black"), WHITE, la, "mm", shadow=6)
    hb = clamp((t - 1.8) / 0.4) * (1 - clamp((t - sq) / 0.3))
    text_a(img, (W / 2, 1330), "▲ " + sc.get("he", "") + " ▲", F("disp", 44, "Black"), (255, 150, 60), hb, "mm", shadow=6)
    if t > sq:   # flash + shock ring + shake
        f_ = max(0, 1 - (t - sq - 0.3) / 0.9)
        ring = Image.new("RGBA", (W, H), (0, 0, 0, 0)); rr_ = 60 + 1400 * clamp((t - sq - 0.25) / 1.1)
        ImageDraw.Draw(ring).ellipse([cx - rr_, cy - rr_, cx + rr_, cy + rr_], outline=(255, 240, 200, int(220 * f_)), width=30)
        img.alpha_composite(ring.filter(ImageFilter.GaussianBlur(8)))
        if t > sq + 0.3:
            fl = max(0, 1 - (t - sq - 0.3) / 0.7); img.alpha_composite(Image.new("RGBA", (W, H), (255, 250, 235, int(255 * fl))))
        if t > sq + 0.9:
            text_a(img, (W / 2, 330), sc.get("boom1", "NUCLEAR"), F("anton", 140), T["alert"], clamp((t - sq - 0.9) / 0.2), "mm", shadow=12)
            text_a(img, (W / 2, 470), sc.get("boom2", "EXPLOSION"), fit_font("anton", 140, sc.get("boom2", "EXPLOSION"), W - 100), WHITE, clamp((t - sq - 1.0) / 0.2), "mm", shadow=12)
    chrome(img, tg)

def factory_icon(d, x, y, w, h, tg, lit=(255, 200, 80)):
    """Saw-tooth factory silhouette with two stacks; (x, y) = bottom-left."""
    teeth = 4; tw = w * 0.7 / teeth; base = y - h * 0.45
    pts = [(x, y), (x, base)]
    for i in range(teeth): pts += [(x + i * tw, base - h * 0.25), (x + (i + 1) * tw, base)]
    pts += [(x + w * 0.7, base), (x + w * 0.7, y - h * 0.55), (x + w, y - h * 0.55), (x + w, y)]
    d.polygon(pts, fill=(30, 36, 32, 255), outline=(110, 130, 110, 255))
    for sx in (x + w * 0.76, x + w * 0.9):
        d.rectangle([sx, y - h, sx + w * 0.06, y - h * 0.55], fill=(36, 42, 38, 255), outline=(110, 130, 110, 255))
    for i in range(9):
        wx = x + 30 + i * (w - 60) / 9; on = (math.sin(i * 2.3 + tg * 3) > -0.3)
        d.rectangle([wx, y - h * 0.3, wx + 34, y - h * 0.18], fill=(lit + (230,)) if on else (60, 60, 50, 255))

def sc_p_factory(img, sc, t, D, tg, k):
    a = clamp(t / 0.3)
    text_a(img, (W / 2, 300), sc.get("place", ""), F("mono", 38), T["accent2"], a, "mm", shadow=4)
    text_a(img, (W / 2, 350), sc.get("years", ""), F("mono", 32), MUTED, a, "mm")
    g = ease(clamp((t - 0.3) / 1.6))
    lo, hi = 1000 * g, 2000 * g
    text_a(img, (W / 2, 500), f"{lo:,.0f} – {hi:,.0f}", fit_font("anton", 170, "2,000 – 2,000", W - 100), T["accent"], a, "mm", shadow=12)
    text_a(img, (W / 2, 625), sc.get("big_sub", ""), F("disp", 54, "Black"), WHITE, clamp((t - 0.6) / 0.3), "mm", shadow=6)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for j in range(4):   # smoke puffs
        ph = (tg * 0.35 + j / 4) % 1
        for sx in (130 + 600 * 0.76, 130 + 600 * 0.9):
            r_ = 18 + 40 * ph; d.ellipse([sx + 18 - r_, 760 - 330 * ph - r_, sx + 18 + r_, 760 - 330 * ph + r_], fill=(120, 130, 120, int(110 * (1 - ph))))
    lay = lay.filter(ImageFilter.GaussianBlur(6)); d = ImageDraw.Draw(lay)
    factory_icon(d, 130, 1120, 600, 360, tg)
    d.rectangle([100, 1130, W - 60, 1150], fill=(70, 80, 72, 255))
    for i in range(14):
        x = 120 + ((tg * 160 + i * 75) % (W - 160)); d.ellipse([x - 4, 1132, x + 4, 1148], fill=(40, 44, 40, 255))
    paste_a(img, lay, (0, 0), a)
    for i in range(6):   # pits rolling out of the factory on the belt
        x = 700 + ((tg * 160 + i * 70) % 340)
        draw_pit(img, x, 1100, 26, tg + i, a * clamp((x - 700) / 40), heat=0.6, beat=False)
    chrome(img, tg)

def sc_p_years(img, sc, t, D, tg, k):
    """Year counter racing past a flat line of 'few pits', then the first new pit with its diamond stamp."""
    da = sc.get("date_at", 4.0); y0, y1 = sc.get("from", 1989), sc.get("to", 2024)
    p = ease_io(clamp((t - 0.3) / max(0.5, da - 0.8)))
    yr = int(round(y0 + (y1 - y0) * p))
    a = clamp(t / 0.3) * (1 - clamp((t - da) / 0.3))
    text_a(img, (W / 2, 420), str(yr), F("anton", 230), WHITE, a, "mm", shadow=12)
    x0, x1, gy = 110, W - 110, 900
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.line([x0, gy, x1, gy], fill=(80, 90, 80, 200), width=3)
    pts = [(x0, gy - 300), (x0 + 30, gy - 300), (x0 + 60, gy - 8)]
    for i in range(1, 60):
        xx = x0 + 60 + i * (x1 - x0 - 60) / 60; bump = 22 if 22 < i < 30 else 0
        pts.append((xx, gy - 8 - bump * abs(math.sin(i))))
    n = max(2, int(len(pts) * clamp(p * 1.02)))
    d.line(pts[:n], fill=T["accent"] + (255,), width=8, joint="curve")
    paste_a(img, lay, (0, 0), a)
    text_a(img, (x0, gy - 330), "1980s: THOUSANDS", F("mono", 28), MUTED, a * clamp(t / 0.6), "la")
    text_a(img, (W / 2, gy + 60), sc.get("flat", ""), F("disp", 46, "Black"), T["accent"], a * clamp((t - 1.2) / 0.4), "mm", shadow=6)
    if t > da:
        q = back(clamp((t - da) / 0.5)); cx, cy = W / 2, 800
        rd = 300 * clamp(q, 0.3, 1.1)
        dl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(dl)
        dd.polygon([(cx, cy - rd), (cx + rd, cy), (cx, cy + rd), (cx - rd, cy)], outline=T["accent"] + (255,), width=10)
        img.alpha_composite(dl)
        draw_pit(img, cx, cy, int(150 * clamp(q, 0.3, 1.05)), tg)
        text_a(img, (W / 2, 330), sc.get("date", ""), F("anton", 130), T["alert"], clamp((t - da) / 0.2), "mm", shadow=10)
        text_a(img, (W / 2, 1180), sc.get("what", ""), fit_font("anton", 80, sc.get("what", ""), W - 120), WHITE, clamp((t - da - 0.3) / 0.3), "mm", shadow=8)
        text_a(img, (W / 2, 1270), sc.get("where", ""), F("mono", 32), T["accent2"], clamp((t - da - 0.5) / 0.3), "mm")
    chrome(img, tg)

def sc_p_ramp(img, sc, t, D, tg, k):
    """Three rising bars: pits per year targets, the last (biggest) one in red with the siren."""
    bars = sc["bars"]; ats = sc.get("bar_at", [1.0 + 2.0 * i for i in range(len(bars))]); mx = max(b[1] for b in bars)
    text_a(img, (W / 2, 310), sc.get("kicker", ""), F("mono", 38), T["accent2"], clamp(t / 0.3), "mm", shadow=4)
    base, top = 1250, 520; bw = 230
    for i, (yr, v, lab) in enumerate(bars):
        x = W / 2 + (i - 1) * 310; g = ease(clamp((t - ats[i]) / 0.8)); last = i == len(bars) - 1
        col = T["alert"] if last else T["accent"]
        rect_a(img, (x - bw / 2, top, x + bw / 2, base), (20, 24, 22), 0.6, 18, (60, 70, 60), 2)
        if g > 0:
            h = (base - top) * v / mx * g
            rect_a(img, (x - bw / 2 + 8, base - h, x + bw / 2 - 8, base - 6), col, 0.92, 14)
            text_a(img, (x, base - h - 70), f"{v * g:.0f}", F("anton", 110 if last else 92), col, clamp((t - ats[i]) / 0.2), "mm", shadow=8)
        text_a(img, (x, base + 50), yr, F("anton", 64), WHITE, clamp((t - ats[i] + 0.4) / 0.3), "mm")
        text_a(img, (x, base + 110), lab, fit_font("disp", 30, lab, 290, "Black"), MUTED, clamp((t - ats[i]) / 0.3), "mm")
    alarm(img, tg, clamp((t - ats[-1]) / 0.5))
    chrome(img, tg)

def bolt(d, x, y, s, col):
    d.polygon([(x + 8 * s, y - 40 * s), (x - 16 * s, y + 6 * s), (x, y + 6 * s), (x - 8 * s, y + 40 * s), (x + 18 * s, y - 8 * s), (x + 2 * s, y - 8 * s)], fill=col + (255,))

def sc_p_mox(img, sc, t, D, tg, k):
    """The twist: the half-built 'bombs -> electricity' plant becomes the bomb-core factory."""
    na, sa, ca = sc.get("now_at", 4.0), sc.get("stamp_at", 7.0), sc.get("cost_at", 9.0)
    a = clamp(t / 0.3)
    text_a(img, (W / 2, 300), sc.get("place", ""), fit_font("mono", 34, sc.get("place", ""), W - 120), T["accent2"], a, "mm", shadow=4)
    red = clamp((t - na) / 0.6)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    bx0, by0, bx1, by1 = 170, 500, 910, 830
    d.rectangle([bx0, by0, bx1, by1], fill=(32, 36, 34, 255), outline=(120, 130, 120, 255), width=4)
    for i in range(6):   # unfinished: open grid at the right end
        x = bx0 + 40 + i * 120
        for j in range(2):
            y = by0 + 60 + j * 130
            c = (int(70 + 185 * red), int(70 - 30 * red), int(60 - 30 * red), 255) if i < 5 else (0, 0, 0, 0)
            if i < 5: d.rectangle([x, y, x + 80, y + 70], fill=c)
            else: d.rectangle([x, y, x + 80, y + 70], outline=(120, 130, 120, 255), width=3)
    d.line([bx1 - 40, by0, bx1 - 40, by0 - 120], fill=(200, 170, 60, 255), width=10)   # crane
    d.line([bx1 - 220, by0 - 120, bx1 + 60, by0 - 120], fill=(200, 170, 60, 255), width=10)
    d.line([bx1 - 180, by0 - 120, bx1 - 180, by0 - 40 + 10 * math.sin(tg * 2)], fill=(160, 160, 150, 255), width=3)
    paste_a(img, lay, (0, 0), a)
    # the original purpose
    wa = clamp((t - 0.6) / 0.4)
    rect_a(img, (110, 880, W - 110, 1060), (12, 40, 24), 0.9 * wa, 22, (90, 220, 120), 3)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    bomb_icon(d, 190, 980, 1.3, (200, 200, 190)); d.line([240, 970, 290, 970], fill=(90, 220, 120, 255), width=6)
    d.polygon([(290, 958), (306, 970), (290, 982)], fill=(90, 220, 120, 255)); bolt(d, 335, 970, 1.2, (255, 220, 60))
    paste_a(img, lay, (0, 0), wa)
    text_a(img, (620, 940), sc.get("was", ""), fit_font("disp", 36, sc.get("was", ""), 560, "Black"), WHITE, wa, "mm")
    text_a(img, (620, 1000), sc.get("was2", ""), fit_font("disp", 36, sc.get("was2", ""), 560, "Black"), (130, 235, 150), wa, "mm")
    if t > na:
        q = clamp((t - na) / 0.3); d = ImageDraw.Draw(img)
        d.line([120, 890, 120 + (W - 240) * q, 1050], fill=T["alert"] + (255,), width=14)
        d.line([W - 120, 890, W - 120 - (W - 240) * q, 1050], fill=T["alert"] + (255,), width=14)
        text_a(img, (W / 2, 1140), sc.get("now", ""), fit_font("anton", 100, sc.get("now", ""), W - 120), T["alert"], clamp((t - na - 0.2) / 0.25), "mm", shadow=10)
        draw_pit(img, bx0 + 80 + 360, by0 + 165, int(60 * clamp((t - na) / 0.5)), tg, clamp((t - na) / 0.4))
    if t > sa: slam(img, stamp_img(sc.get("stamp", ""), 66, rot=-8), W / 2, 670, sa, t, max_w=W - 120)
    if t > ca:
        g = back(clamp((t - ca) / 0.45)); s_ = clamp(g, 0.3, 1.1)
        rect_a(img, (W / 2 - 330 * s_, 1290 - 85 * s_, W / 2 + 330 * s_, 1290 + 85 * s_), (40, 30, 6), 0.95, 24, T["accent"], 5)
        text_a(img, (W / 2, 1270), sc.get("cost", ""), F("anton", int(110 * s_)), T["accent"], clamp((t - ca) / 0.15), "mm", shadow=8)
        text_a(img, (W / 2, 1345), sc.get("cost_sub", ""), F("mono", 26), WHITE, clamp((t - ca - 0.2) / 0.2), "mm")
    chrome(img, tg)

def sc_p_debate(img, sc, t, D, tg, k):
    ra = sc.get("right_at", 4.0)
    for side, (lines, at, col, x0) in enumerate([(sc["left"], 0.2, T["accent2"], 70), (sc["right"], ra, T["accent"], W / 2 + 15)]):
        a = clamp((t - at) / 0.35); dx = (1 - ease(a)) * (-120 if side == 0 else 120)
        x1 = x0 + W / 2 - 85
        rect_a(img, (x0 + dx, 380, x1 + dx, 1120), (16, 20, 18), 0.92 * a, 26, col, 4)
        cx = (x0 + x1) / 2 + dx
        if side == 0: paste_a(img, R.flag("US", 150), (cx - 75, 430), a)
        elif a > 0: atom(img, cx, 500, 70, tg, a, col)
        text_a(img, (cx, 640), lines[0], fit_font("anton", 58, lines[0], x1 - x0 - 40), col, a, "mm", shadow=6)
        for j, s in enumerate(lines[1:]):
            words = s.split(); half = (len(words) + 1) // 2
            for m, part in enumerate([" ".join(words[:half]), " ".join(words[half:])]):
                text_a(img, (cx, 760 + j * 170 + m * 62), part, fit_font("disp", 48, part, x1 - x0 - 50, "Black"), WHITE, clamp((t - at - 0.3 - j * 0.6) / 0.3), "mm")
    va = clamp((t - ra) / 0.3)
    if va > 0:
        rect_a(img, (W / 2 - 60, 690, W / 2 + 60, 810), T["alert"], va, 60)
        text_a(img, (W / 2, 748), "VS", F("anton", 64), (255, 255, 255), va, "mm")
    text_a(img, (W / 2, 1180), sc.get("note", ""), fit_font("disp", 32, sc.get("note", ""), W - 140, "Medium"), MUTED, clamp((t - ra - 1.5) / 0.4), "mm")
    chrome(img, tg)

def sc_p_treaty(img, sc, t, D, tg, k):
    """The treaty paper tears in two, EXPIRED stamp, then NO LIMITS under the siren."""
    ta, sa, ba = sc.get("tear_at", 2.0), sc.get("stamp_at", 2.6), sc.get("big_at", 5.0)
    pw, ph = 760, 600; card = paper(pw, ph).copy(); d = ImageDraw.Draw(card)
    d.rectangle([0, 0, pw, 60], fill=(160, 40, 40, 255)); d.text((pw / 2, 30), "TREATY", font=F("mono", 30), fill=(250, 240, 230), anchor="mm")
    d.text((pw / 2, 170), sc.get("title", ""), font=F("anton", 120), fill=(30, 26, 22), anchor="mm")
    d.text((pw / 2, 280), sc.get("years", ""), font=F("anton", 64), fill=(90, 70, 50), anchor="mm")
    d.text((pw / 2, 360), sc.get("sub", ""), font=fit_font("disp", 34, sc.get("sub", ""), pw - 60, "Black"), fill=(60, 50, 40), anchor="mm")
    for j in range(4): d.line([60, 430 + j * 36, pw - 60 - (j * 70) % 200, 430 + j * 36], fill=(150, 135, 110), width=4)
    tq = ease(clamp((t - ta) / 0.7)); a = clamp(t / 0.3); bx, by = W / 2 - pw / 2, 330
    if tq <= 0:
        paste_a(img, card, (bx, by), a)
    else:   # zig-zag tear down the middle, halves drift apart and tilt
        m = Image.new("L", (pw, ph), 0); md = ImageDraw.Draw(m)
        zz = [(pw / 2 + (18 if j % 2 else -18), j * ph / 14) for j in range(15)]
        md.polygon([(0, 0)] + zz + [(0, ph)], fill=255)
        L_ = card.copy(); L_.putalpha(Image.fromarray(np.minimum(np.asarray(card.getchannel("A")), np.asarray(m))))
        Rm = Image.fromarray(255 - np.asarray(m)); R_ = card.copy(); R_.putalpha(Image.fromarray(np.minimum(np.asarray(card.getchannel("A")), np.asarray(Rm))))
        Lr = L_.rotate(8 * tq, expand=True, resample=Image.BICUBIC); Rr = R_.rotate(-8 * tq, expand=True, resample=Image.BICUBIC)
        paste_a(img, Lr, (bx - 90 * tq - (Lr.width - pw) / 2, by + 30 * tq - (Lr.height - ph) / 2), a)
        paste_a(img, Rr, (bx + 90 * tq - (Rr.width - pw) / 2, by + 30 * tq - (Rr.height - ph) / 2), a)
    if t > sa: slam(img, stamp_img(sc.get("stamp", ""), 70), W / 2, by + ph / 2 + 40, sa, t, max_w=W - 140)
    if t > ba:
        g = back(clamp((t - ba) / 0.5)); s_ = clamp(g, 0.3, 1.1)
        text_a(img, (W / 2, 1110), sc.get("big", ""), F("anton", int(190 * s_)), T["alert"], clamp((t - ba) / 0.15), "mm", shadow=14)
        text_a(img, (W / 2, 1260), sc.get("big_sub", ""), F("disp", 50, "Black"), WHITE, clamp((t - ba - 0.3) / 0.3), "mm", shadow=6)
        alarm(img, tg, clamp((t - ba) / 0.4))
    chrome(img, tg)

R.SCENE_FN.update({"p_hook": sc_p_hook, "p_pit": sc_p_pit, "p_factory": sc_p_factory, "p_years": sc_p_years, "p_ramp": sc_p_ramp,
                   "p_mox": sc_p_mox, "p_debate": sc_p_debate, "p_treaty": sc_p_treaty})


# ---------------------------------------------------------------- reel 025: newsroom "Reality Check" (light theme "news")
def rcol(name):
    if isinstance(name, (list, tuple)): return tuple(name)
    return {"alert": T["alert"], "amber": T.get("amber", (206, 132, 0)), "green": T.get("green", (14, 132, 78)),
            "navy": T["accent"], "WHITE": WHITE}.get(name, T["accent"])

def rc_chrome(img, tg):
    """Newsroom furniture: red REALITY CHECK badge with a live dot, hairline rule."""
    f = F("anton", 44); w = ImageDraw.Draw(Image.new("L", (1, 1))).textlength("REALITY CHECK", font=f)
    rect_a(img, (60, 118, 60 + w + 86, 190), T["alert"], 1, 10)
    p = 0.5 + 0.5 * math.sin(tg * 5)
    d = ImageDraw.Draw(img); d.ellipse([82, 142, 104, 164], fill=(255, 255, 255, int(120 + 135 * p)))
    text_a(img, (120, 154), "REALITY CHECK", f, (255, 255, 255), 1, "lm")
    text_a(img, (60, 218), "OFFICIAL DATA · VERIFIED SOURCES", F("mono", 24), MUTED, 1, "lm")
    rect_a(img, (60, 244, W - 60, 247), T["accent"], 0.9)

def verdict_banner(img, t, at, label, col, sub="", y=1265):
    if at is None or t < at: return
    g = back(clamp((t - at) / 0.4)); s_ = clamp(g, 0.2, 1.06); col = rcol(col)
    cx = W / 2; hw = (W - 120) / 2 * s_; hh = 75 * s_
    card(img, (cx - hw, y - hh, cx + hw, y + hh), clamp((t - at) / 0.15), 18, (255, 255, 255), col)
    rect_a(img, (cx - hw, y - hh, cx - hw + 230 * s_, y + hh), col, clamp((t - at) / 0.15), 18)
    text_a(img, (cx - hw + 115 * s_, y), "VERDICT", F("anton", int(46 * s_) or 1), (255, 255, 255), clamp((t - at) / 0.15), "mm")
    tx0 = cx - hw + 260 * s_; tw = 2 * hw - 290 * s_
    text_a(img, (tx0, y - (22 if sub else 0) * s_), label, fit_font("anton", int(70 * s_) or 1, label, max(10, tw)), col, clamp((t - at - 0.1) / 0.2), "lm")
    if sub: text_a(img, (tx0, y + 40 * s_), sub, fit_font("disp", int(30 * s_) or 1, sub, max(10, tw), "Bold"), MUTED, clamp((t - at - 0.2) / 0.2), "lm")

def wrap_lines(s, f, maxw):
    words = s.split(); lines = []; cur = ""
    meas = ImageDraw.Draw(Image.new("L", (1, 1)))
    for w_ in words:
        tryl = (cur + " " + w_).strip()
        if meas.textlength(tryl, font=f) <= maxw: cur = tryl
        else: lines.append(cur); cur = w_
    if cur: lines.append(cur)
    return lines

def sc_rc_hook(img, sc, t, D, tg, k):
    rc_chrome(img, tg)
    ats = sc.get("claim_at", [0.0, 1.5, 3.0]); qa = sc.get("q_at", 4.5)
    for i, (lab, col) in enumerate(sc["claims"]):
        a = 1.0 if i == 0 else clamp((t - ats[i]) / 0.3); dx = (1 - ease(a)) * 200
        y = 420 + i * 210; c = rcol(col)
        card(img, (80 + dx, y - 80, W - 80 + dx, y + 80), a, 20)
        rect_a(img, (80 + dx, y - 80, 96 + dx, y + 80), c, a, 4)
        text_a(img, (130 + dx, y), lab, fit_font("anton", 84, lab, W - 300), c, a, "lm")
        text_a(img, (W - 120 + dx, y), "?", F("anton", 90), (190, 196, 210), a, "rm")
    if t > qa:
        a = clamp((t - qa) / 0.35)
        text_a(img, (W / 2, 1110), sc.get("q", ""), fit_font("anton", 92, sc.get("q", ""), W - 120), T["accent"], a, "mm")
        rect_a(img, (W / 2 - 160 * ease(a), 1190, W / 2 + 160 * ease(a), 1196), T["alert"], a)
        text_a(img, (W / 2, 1250), "OFFICIAL DATA · IMF · GOVT SURVEYS", F("mono", 28), MUTED, clamp((t - qa - 0.3) / 0.3), "mm")
    chrome(img, tg)

def sc_rc_claim(img, sc, t, D, tg, k):
    rc_chrome(img, tg)
    c = rcol(sc.get("col", "navy")); a = clamp(t / 0.35); dy = (1 - ease(a)) * 60
    x0, x1, y0, y1 = 80, W - 80, 320 + dy, 1240 + dy
    card(img, (x0, y0, x1, y1), a, 26); rect_a(img, (x0, y0, x0 + 18, y1), c, a, 6)
    text_a(img, (x0 + 70, y0 + 80), sc.get("n", ""), F("mono", 32), c, a, "lm")
    text_a(img, (x0 + 60, y0 + 190), "“", F("anton", 220), c, 0.25 * a, "lm")
    f = F("disp", 66, "Bold"); lines = wrap_lines(sc["quote"], f, x1 - x0 - 140)
    nwords = len(sc["quote"].split()); shown = int(nwords * clamp((t - 0.3) / 1.6)) + 1; cnt = 0
    for j, ln in enumerate(lines):
        ws = ln.split(); vis = " ".join(ws[:max(0, shown - cnt)]); cnt += len(ws)
        if vis: text_a(img, (x0 + 70, y0 + 300 + j * 86), vis, f, (22, 30, 44), a, "lm")
    yb = y0 + 300 + len(lines) * 86 + 40
    q = clamp((t - 1.2) / 0.4)
    rect_a(img, (x0 + 70, yb, x0 + 70 + 220 * ease(q), yb + 4), c, q)
    text_a(img, (x0 + 70, yb + 70), sc.get("who", ""), fit_font("anton", 70, sc.get("who", ""), x1 - x0 - 140), T["accent"], q, "lm")
    text_a(img, (x0 + 70, yb + 135), sc.get("role", ""), fit_font("disp", 36, sc.get("role", ""), x1 - x0 - 140, "Bold"), MUTED, q, "lm")
    text_a(img, (x0 + 70, yb + 190), sc.get("when", ""), fit_font("mono", 28, sc.get("when", ""), x1 - x0 - 140), MUTED, clamp((t - 1.5) / 0.4), "lm")
    chrome(img, tg)

def bars_h(img, rows, x0, y0, t, at, maxv, w=560, hl=0):
    for i, (name, v, code) in enumerate(rows):
        y = y0 + i * 112; g = ease(clamp((t - at - i * 0.25) / 0.7)); a = clamp((t - at - i * 0.25) / 0.3)
        if code: paste_a(img, R.flag(code, 64), (x0, y - 30), a)
        text_a(img, (x0 + 84, y), name, F("anton", 46), (40, 48, 64), a, "lm")
        bx = x0 + 300; rect_a(img, (bx, y - 26, bx + w, y + 26), (226, 230, 238), a, 10)
        col = rcol("green") if i == hl else (150, 158, 176)
        if g > 0: rect_a(img, (bx, y - 26, bx + w * v / maxv * g, y + 26), col, a, 10)
        text_a(img, (bx + w * v / maxv * g + 18, y), f"{v * g:.1f}%", F("anton", 48), col, a, "lm")

def sc_rc_growth(img, sc, t, D, tg, k):
    rc_chrome(img, tg)
    a = clamp(t / 0.3); g = ease(clamp((t - 0.2) / 1.4))
    card(img, (80, 300, W - 80, 660), a, 24)
    text_a(img, (W / 2, 450), f"{sc['big'] * g:.1f}%", F("anton", 210), rcol("green"), a, "mm")
    text_a(img, (W / 2, 575), sc.get("big_lbl", ""), fit_font("disp", 40, sc.get("big_lbl", ""), W - 220, "Bold"), (40, 48, 64), a, "mm")
    text_a(img, (W / 2, 625), sc.get("big_src", ""), F("mono", 24), MUTED, a, "mm")
    ba = sc.get("bars_at", 3.0); qa = clamp((t - ba + 0.3) / 0.3)
    text_a(img, (90, 740), sc.get("bars_lbl", ""), fit_font("disp", 36, sc.get("bars_lbl", ""), W - 180, "Bold"), T["accent"], qa, "lm")
    bars_h(img, sc["bars"], 90, 830, t, ba, max(b[1] for b in sc["bars"]) * 1.05, w=520)
    text_a(img, (90, 1150), sc.get("bars_src", ""), fit_font("mono", 24, sc.get("bars_src", ""), W - 180), MUTED, qa, "lm")
    verdict_banner(img, t, sc.get("verdict_at"), sc.get("verdict", ""), sc.get("vcol", "alert"), sc.get("vsub", ""))
    chrome(img, tg)

def sc_rc_jobs(img, sc, t, D, tg, k):
    rc_chrome(img, tg)
    L = sc["left"]; a = clamp(t / 0.3)
    card(img, (80, 290, W - 80, 450), a, 22); rect_a(img, (80, 290, 96, 450), rcol(L[3]), a, 4)
    text_a(img, (130, 370), L[0], F("anton", 96), rcol(L[3]), a, "lm")
    text_a(img, (380, 345), L[1], F("anton", 44), (40, 48, 64), a, "lm")
    text_a(img, (380, 400), L[2], F("disp", 34, "Bold"), MUTED, a, "lm")
    ja = sc.get("jobs_at", 3.0)
    if t > ja - 0.3:
        b = clamp((t - ja + 0.3) / 0.3); g = ease(clamp((t - ja) / 1.4)); v = sc["big_from"] + (sc["big"] - sc["big_from"]) * g
        card(img, (80, 500, W - 80, 960), b, 24); rect_a(img, (80, 500, 96, 960), rcol("amber"), b, 4)
        text_a(img, (W / 2, 560), sc.get("big_lbl", ""), fit_font("disp", 36, sc.get("big_lbl", ""), W - 220, "Bold"), T["accent"], b, "mm")
        text_a(img, (W / 2, 720), f"{v:.1f}%", F("anton", 220), rcol("amber"), b, "mm")
        text_a(img, (W / 2, 860), sc.get("big_sub", ""), F("disp", 40, "Bold"), (40, 48, 64), b, "mm")
        text_a(img, (W / 2, 915), sc.get("big_src", ""), F("mono", 24), MUTED, b, "mm")
    ua = sc.get("urban_at", 6.0)
    if t > ua:
        u = back(clamp((t - ua) / 0.4)); s_ = clamp(u, 0.3, 1.08)
        card(img, (W / 2 - 330 * s_, 1060 - 65 * s_, W / 2 + 330 * s_, 1060 + 65 * s_), clamp((t - ua) / 0.15), 20)
        text_a(img, (W / 2 - 300 * s_, 1060), sc.get("urban", ""), F("anton", int(84 * s_)), T["alert"], clamp((t - ua) / 0.15), "lm")
        text_a(img, (W / 2 - 110 * s_, 1060), sc.get("urban_lbl", ""), fit_font("disp", int(30 * s_), sc.get("urban_lbl", ""), int(420 * s_), "Bold"), (40, 48, 64), clamp((t - ua) / 0.2), "lm")
    verdict_banner(img, t, sc.get("verdict_at"), sc.get("verdict", ""), sc.get("vcol", "amber"), sc.get("vsub", ""))
    chrome(img, tg)

def sc_rc_picture(img, sc, t, D, tg, k):
    rc_chrome(img, tg)
    ra, ka, pa = sc.get("rupee_at", 1.0), sc.get("rank_at", 4.0), sc.get("pc_at", 8.0)
    # 1) rupee line
    a = clamp((t - ra + 0.4) / 0.3)
    card(img, (80, 280, W - 80, 640), a, 22)
    text_a(img, (110, 320), sc.get("rupee_lbl", ""), F("disp", 34, "Bold"), T["accent"], a, "lm")
    text_a(img, (W - 110, 320), "higher = weaker rupee", F("mono", 22), MUTED, a, "rm")
    pts = sc["rupee"]; lo, hi = 82, 99; gx0, gx1, gy0, gy1 = 160, W - 180, 590, 380
    P = [(gx0 + (gx1 - gx0) * p[0] / (len(pts) - 1), gy0 + (gy1 - gy0) * (p[1] - lo) / (hi - lo)) for p in pts]
    g = clamp((t - ra) / 1.6); n = g * (len(P) - 1)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    seg = [P[0]]
    for j in range(1, len(P)):
        if n >= j: seg.append(P[j])
        elif n > j - 1:
            f_ = n - (j - 1); seg.append((P[j - 1][0] + (P[j][0] - P[j - 1][0]) * f_, P[j - 1][1] + (P[j][1] - P[j - 1][1]) * f_)); break
    if len(seg) > 1: d.line(seg, fill=T["accent"] + (255,), width=8, joint="curve")
    paste_a(img, lay, (0, 0), a)
    for j, (x, y) in enumerate(P):
        if n >= j - 0.05:
            rec = abs(pts[j][1] - max(p[1] for p in pts)) < 1e-6; c = T["alert"] if rec else T["accent"]
            ImageDraw.Draw(img).ellipse([x - 12, y - 12, x + 12, y + 12], fill=c + (255,))
            text_a(img, (x, y - 40), f"{pts[j][1]:.2f}".rstrip("0").rstrip("."), F("anton", 40), c, 1, "mm")
            text_a(img, (x, 615), pts[j][2], fit_font("mono", 20, pts[j][2], 230), MUTED, 1, "mm")
    # 2) rank
    b = clamp((t - ka) / 0.3)
    if b > 0:
        card(img, (80, 680, W - 80, 960), b, 22)
        text_a(img, (110, 720), sc.get("rank_lbl", ""), F("disp", 34, "Bold"), T["accent"], b, "lm")
        for j, (yr, rk, note) in enumerate(sc["rank"]):
            q = back(clamp((t - ka - j * 0.5) / 0.4)); x = 260 + j * 280; c = T["alert"] if rk > 4 else rcol("green")
            if q > 0:
                rr = 62 * clamp(q, 0.3, 1.1)
                ImageDraw.Draw(img).ellipse([x - rr, 830 - rr, x + rr, 830 + rr], fill=c + (255,))
                text_a(img, (x, 830), f"#{rk}", F("anton", int(64 * clamp(q, 0.3, 1.1))), (255, 255, 255), 1, "mm")
                text_a(img, (x, 920), f"{yr} · {note}", F("mono", 22), MUTED, clamp(q, 0, 1), "mm")
            if j > 0 and q > 0:
                ImageDraw.Draw(img).line([x - 210, 830, x - 80, 830], fill=(170, 176, 190, 255), width=5)
    # 3) per capita
    c_ = clamp((t - pa) / 0.3)
    if c_ > 0:
        card(img, (80, 1000, W - 80, 1150), c_, 22)
        text_a(img, (120, 1075), sc.get("pc", ""), F("anton", 92), T["alert"], c_, "lm")
        text_a(img, (430, 1075), sc.get("pc_lbl", ""), fit_font("disp", 32, sc.get("pc_lbl", ""), W - 560, "Bold"), (40, 48, 64), c_, "lm")
    verdict_banner(img, t, sc.get("verdict_at"), sc.get("verdict", ""), sc.get("vcol", "green"), sc.get("vsub", ""))
    chrome(img, tg)

def sc_rc_score(img, sc, t, D, tg, k):
    rc_chrome(img, tg)
    text_a(img, (W / 2, 330), "THE VERDICT", F("anton", 110), T["accent"], clamp(t / 0.3), "mm")
    ats = sc.get("row_at", [0.4, 1.0, 1.6])
    for i, (claim, who, ver, col) in enumerate(sc["rows"]):
        a = clamp((t - ats[i]) / 0.3); dx = (1 - ease(a)) * 160; y = 520 + i * 230; c = rcol(col)
        card(img, (80 + dx, y - 95, W - 80 + dx, y + 95), a, 22); rect_a(img, (80 + dx, y - 95, 98 + dx, y + 95), c, a, 4)
        text_a(img, (130 + dx, y - 38), claim, fit_font("anton", 58, claim, 560), (30, 38, 54), a, "lm")
        text_a(img, (130 + dx, y + 30), who, F("mono", 28), MUTED, a, "lm")
        f = fit_font("anton", 40, ver, 300); lines = ver.split(" · ")
        for m, ln in enumerate(lines):
            text_a(img, (W - 110 + dx, y + (m - (len(lines) - 1) / 2) * 50), ln, fit_font("anton", 44, ln, 330), c, a, "rm")
    la = clamp((t - sc.get("line_at", 3.0)) / 0.4)
    text_a(img, (W / 2, 1260), sc.get("line", ""), fit_font("disp", 54, sc.get("line", ""), W - 140, "Black"), T["accent"], la, "mm")
    rect_a(img, (W / 2 - 200 * ease(la), 1310, W / 2 + 200 * ease(la), 1315), T["alert"], la)
    chrome(img, tg)

R.SCENE_FN.update({"rc_hook": sc_rc_hook, "rc_claim": sc_rc_claim, "rc_growth": sc_rc_growth, "rc_jobs": sc_rc_jobs,
                   "rc_picture": sc_rc_picture, "rc_score": sc_rc_score})

if __name__ == "__main__":
    R.main()
