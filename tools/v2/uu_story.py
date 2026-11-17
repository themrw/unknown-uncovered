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
    for i, ln in enumerate(sc.get("lines", [])):
        st = 1.0 + i * 0.7
        if R.LOOK == "cinematic":
            rise_line(img, ln, W / 2, y0 + 330 + i * 70, fit_font("disp", 54, ln, W - 120, "Bold"), t - st)
        else:
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
    hud_text(img, (60, 250), sc.get("hud", "SAT-PASS  //  TARGET: POKHRAN  27.09°N 71.75°E"), 24, a=a)
    hud_text(img, (60, 288), f"T+{tg:06.2f}s   ORBIT 400 KM   RES 0.3 M", 22, MUTED, a)
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
                d.polygon(pts, fill=T["land"] + (int(200 * a),))
                n = max(2, int(len(pts) * draw_p)); d.line(pts[:n], fill=T["accent"] + (255,), width=4)
            else:
                d.polygon(pts, fill=(22, 20, 30, int(160 * a)), outline=T["land_edge"] + (int(70 * a),))
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
        if 60 < lx < W - 60 and 300 < ly < 1000: text_a(img, (lx, ly), lab, F("mono", 24), MUTED, a * (1 - z * 0.5), "mm")
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

def sc_dossier(img, sc, t, D, tg, k):
    """A classified file slides in, lines are typed, then a red stamp slams down."""
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
    x = W / 2 - card.width / 2 + (1 - a) * 300 + shake * math.sin(t * 90); y = 300 + shake * math.cos(t * 80)
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)), (int(x + 16), int(y + 24)))
    paste_a(img, card, (x, y), a)
    caption(img, sc, t, D, 1180)
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
    if after > 0:   # dust plume + shock ring
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        pr = clamp(after / 2.5)
        for j in range(7):
            rr = 60 + 260 * pr * (0.6 + j * 0.08); yy = hy - 40 - 200 * pr * (j / 6)
            d.ellipse([W / 2 - rr, yy - rr * 0.45, W / 2 + rr, yy + rr * 0.45], fill=(200, 150, 100, int(110 * (1 - pr * 0.6))))
        rw = 80 + 900 * clamp(after / 1.2)
        d.ellipse([W / 2 - rw, hy - rw * 0.08, W / 2 + rw, hy + rw * 0.08], outline=T["accent"] + (int(230 * (1 - clamp(after / 1.2))),), width=8)
        img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(14)))
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

R.SCENE_FN.update({"satellite": sc_satellite, "map": sc_map, "dossier": sc_dossier, "blast": sc_blast})
R.SCENE_FN.update({"iceberg": sc_iceberg})
R.SCENE_FN.update({"photo": sc_photo, "counter": sc_counter, "bulb": sc_bulb})

if __name__ == "__main__":
    R.main()
