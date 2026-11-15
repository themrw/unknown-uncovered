import sys, os, math, json, subprocess
import numpy as np
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 60
F = "/usr/share/fonts/opentype/inter/"
_fc = {}
def font(w, s, disp=False):
    k = (w, s, disp)
    if k not in _fc: _fc[k] = ImageFont.truetype(F + ("InterDisplay-" if disp else "Inter-") + w + ".otf", s)
    return _fc[k]
def dfont(w, s): return font(w, s, True)
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
def mono(s):
    k = ("mono", s)
    if k not in _fc: _fc[k] = ImageFont.truetype(MONO, s)
    return _fc[k]

BG = (6, 10, 12); WHITE = (240, 242, 245); MUTED = (128, 140, 146)
RED = (232, 64, 70); AMBER = (240, 170, 50); HUD = (110, 210, 150); GREEN = (90, 200, 120)

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def back(x):
    x = clamp(x); c = 1.6; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def prog(t, s, d): return ease((t - s) / d)

# ---------- background: tactical topo map + grid + scanlines + vignette (larger, panned) ----------
BW, BH = W + 120, H + 120
def make_bg():
    y, x = np.mgrid[0:BH, 0:BW].astype(np.float32)
    f = (np.sin(x / 210) + np.sin(y / 260 + 1.3) + np.sin((x + y) / 330) + 0.6 * np.sin((x - 1.7 * y) / 150 + 2))
    band = np.abs((f * 3.2) % 1 - 0.5) < 0.035
    img = np.zeros((BH, BW, 3), np.float32) + np.array(BG, np.float32)
    img[band] += np.array([10, 30, 22], np.float32)
    img[(x.astype(int) % 90) == 0] += np.array([8, 18, 16], np.float32)
    img[(y.astype(int) % 90) == 0] += np.array([8, 18, 16], np.float32)
    img[(y.astype(int) % 4) == 0] *= 0.85
    cx, cy = BW / 2, BH * 0.35
    glow = np.exp(-(((x - cx) / 700) ** 2 + ((y - cy) / 600) ** 2))[..., None]
    img += glow * np.array([55, 12, 14], np.float32)
    vig = 1 - 0.55 * np.clip(((x - BW / 2) / (BW * 0.75)) ** 2 + ((y - BH / 2) / (BH * 0.7)) ** 2, 0, 1)
    img *= vig[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
BG_BIG = make_bg()

rng = np.random.default_rng(7)
PART = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(15, 55), rng.uniform(1.5, 4), rng.uniform(.25, .8)) for _ in range(70)]

# ---------- radar ----------
_radar = {}
def radar_parts(R):
    if R in _radar: return _radar[R]
    S = 2 * R + 4
    rings = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(rings); c = S / 2
    for k in range(1, 5):
        r = R * k / 4; d.ellipse([c - r, c - r, c + r, c + r], outline=HUD + (70 if k == 4 else 40,), width=2)
    d.line([c - R, c, c + R, c], fill=HUD + (35,), width=2); d.line([c, c - R, c, c + R], fill=HUD + (35,), width=2)
    for a in range(0, 360, 10):
        ra = math.radians(a); L = 18 if a % 30 == 0 else 8
        d.line([c + (R - L) * math.cos(ra), c + (R - L) * math.sin(ra), c + R * math.cos(ra), c + R * math.sin(ra)], fill=HUD + (90,), width=2)
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32) - c
    ang = (np.arctan2(yy, xx)) % (2 * np.pi); rad = np.hypot(xx, yy)
    trail = np.clip(1 - ((-ang) % (2 * np.pi)) / (np.pi / 2.2), 0, 1) ** 1.8
    a = (trail * 110 * (rad < R)).astype(np.uint8)
    sweep = np.zeros((S, S, 4), np.uint8); sweep[..., 0], sweep[..., 1], sweep[..., 2] = HUD; sweep[..., 3] = a
    sweep = Image.fromarray(sweep, "RGBA")
    ImageDraw.Draw(sweep).line([c, c, c + R, c], fill=HUD + (200,), width=3)
    blips = [(rng.uniform(0.25, 0.9) * R, rng.uniform(0, 2 * math.pi)) for _ in range(7)]
    _radar[R] = (rings, sweep, blips); return _radar[R]

def alpha_mul(im, a):
    if a >= 1: return im
    im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a))); return im

def radar(img, cx, cy, R, tg, alpha=1.0, speed=100):
    if alpha <= 0: return
    rings, sweep, blips = radar_parts(R); S = rings.width
    ang = (tg * speed) % 360
    sw = sweep.rotate(-ang, resample=Image.BILINEAR)
    lay = Image.new("RGBA", (S, S), (0, 0, 0, 0)); lay.alpha_composite(rings); lay.alpha_composite(sw)
    d = ImageDraw.Draw(lay); c = S / 2
    for r, b in blips:
        diff = (math.radians(ang) - b) % (2 * math.pi)
        br = math.exp(-diff * 1.3)
        if br > 0.05:
            x, y = c + r * math.cos(b), c + r * math.sin(b); s = 5 + 4 * br
            d.ellipse([x - s, y - s, x + s, y + s], fill=RED + (int(230 * br),))
    img.alpha_composite(alpha_mul(lay, alpha), (int(cx - c), int(cy - c)))

# ---------- drawing helpers ----------
def text_a(img, xy, s, f, fill, alpha=1.0, anchor="la"):
    if alpha <= 0 or not s: return
    d = ImageDraw.Draw(img)
    l, t, r, b = d.textbbox(xy, s, font=f, anchor=anchor)
    l, t = int(l) - 4, int(t) - 4; r, b = int(r) + 4, int(b) + 4
    layer = Image.new("RGBA", (r - l, b - t), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((xy[0] - l, xy[1] - t), s, font=f, fill=fill + (int(255 * clamp(alpha)),), anchor=anchor)
    cl, ct = -min(l, 0), -min(t, 0)
    if cl or ct: layer = layer.crop((cl, ct, layer.width, layer.height))
    img.alpha_composite(layer, (max(l, 0), max(t, 0)))

def rect_a(img, box, fill, alpha=1.0, r=0, outline=None, width=0):
    if alpha <= 0: return
    x0, y0, x1, y1 = [int(v) for v in box]
    if x1 <= x0 or y1 <= y0: return
    layer = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
    ImageDraw.Draw(layer).rounded_rectangle((0, 0, x1 - x0 - 1, y1 - y0 - 1), radius=r,
        fill=(fill + (int(255 * clamp(alpha)),)) if fill else None,
        outline=(outline + (int(255 * clamp(alpha)),)) if outline else None, width=width)
    img.alpha_composite(layer, (x0, y0))

def brackets(img, box, col, alpha=1.0, L=40, w=4):
    if alpha <= 0: return
    x0, y0, x1, y1 = [int(v) for v in box]
    lay = Image.new("RGBA", (x1 - x0 + 1, y1 - y0 + 1), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    c = col + (int(255 * alpha),); X, Y = x1 - x0, y1 - y0
    for (ax, ay, sx, sy) in [(0, 0, 1, 1), (X, 0, -1, 1), (0, Y, 1, -1), (X, Y, -1, -1)]:
        d.line([ax, ay, ax + sx * L, ay], fill=c, width=w); d.line([ax, ay, ax, ay + sy * L], fill=c, width=w)
    img.alpha_composite(lay, (x0, y0))

EMOJI = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
_flags = {}
def flag(code, w):
    k = (code, w)
    if k not in _flags:
        s = "".join(chr(0x1F1E6 + ord(c) - 65) for c in code)
        im = Image.new("RGBA", (136, 128), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((0, 0), s, font=EMOJI, embedded_color=True)
        _flags[k] = im.resize((w, int(w * 128 / 136)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
    return _flags[k]
def paste_a(img, src, xy, alpha=1.0):
    if alpha > 0: img.alpha_composite(alpha_mul(src, alpha), (int(xy[0]), int(xy[1])))

# ---------- ticker + chrome ----------
TICK = "  WORLD MILITARY SPENDING HITS RECORD $2.89 TRILLION   ///   11TH STRAIGHT YEAR OF GROWTH   ///   EUROPE +14%   ///   ASIA & OCEANIA +8.1%   ///   SOURCE: SIPRI 2026   ///"
def make_ticker():
    f = mono(26); w = int(ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(TICK, font=f))
    im = Image.new("RGBA", (w * 2, 46), (70, 12, 16, 235)); d = ImageDraw.Draw(im)
    d.text((0, 23), TICK, font=f, fill=(255, 220, 220), anchor="lm"); d.text((w, 23), TICK, font=f, fill=(255, 220, 220), anchor="lm")
    return im, w
TICK_IM, TICK_W = make_ticker()

def chrome(img, tg, header=True):
    off = int(tg * 110) % TICK_W
    img.alpha_composite(TICK_IM.crop((off, 0, off + W, 46)), (0, 118))
    rect_a(img, (0, 118, 210, 164), RED)
    text_a(img, (105, 141), "DEFENCE WATCH", mono(22), WHITE, 1, "mm")
    if header:
        rect_a(img, (80, 196, 90, 236), RED)
        text_a(img, (108, 216), "WAR PREPARATION IN THE WORLD", font("Bold", 32), WHITE, 1, "lm")
        if int(tg * 2) % 2 == 0:
            ImageDraw.Draw(img).ellipse([W - 250, 206, W - 230, 226], fill=RED + (255,))
        text_a(img, (W - 220, 216), "2025 DATA", mono(24), WHITE, 1, "lm")
        text_a(img, (80, 262), "Source: SIPRI, April 2026", font("Regular", 28), MUTED, 1, "lm")
    brackets(img, (36, 96, W - 36, 1660), HUD, 0.35, 50, 3)

# ---------- scenes (t = local time, tg = global time) ----------
def typed(s, p): return s[: int(round(len(s) * clamp(p)))]

def s_title(img, t, D, tg):
    radar(img, W / 2, 1000, 500, tg, 0.55 * prog(t, 0, 0.8))
    chrome(img, tg, header=False)
    a = prog(t, 0.1, 0.5)
    rect_a(img, (80, 590, 80 + int(200 * a), 600), RED)
    text_a(img, (80, 620), typed("CLASSIFIED DATA // 2025", prog(t, 0.1, 0.8)), mono(30), HUD, 1)
    for i, (s, f, col, y, st) in enumerate([("WAR", dfont("Black", 230), WHITE, 670, 0.3),
                                            ("PREPARATION", dfont("Black", 138), WHITE, 910, 0.5),
                                            ("IN THE WORLD", dfont("Black", 138), RED, 1070, 0.7)]):
        p = back((t - st) / 0.55); text_a(img, (80 - (1 - p) * 140, y), s, f, col, clamp((t - st) / 0.3))
    text_a(img, (80, 1300), typed("Which countries are arming up the most?", prog(t, 1.3, 1.4)), font("Medium", 46), WHITE, 1)
    codes = ["US", "CN", "RU", "DE", "IN", "GB", "UA", "SA"]
    for i, c in enumerate(codes):
        p = back((t - 2.2 - i * 0.1) / 0.45)
        paste_a(img, flag(c, 100), (80 + i * 116, 1420 + (1 - p) * 60), clamp((t - 2.2 - i * 0.1) / 0.25))

def s_global(img, t, D, tg):
    radar(img, W - 140, 760, 420, tg, 0.5 * prog(t, 0, 0.6))
    chrome(img, tg)
    text_a(img, (80, 380), typed("> GLOBAL MILITARY EXPENDITURE", prog(t, 0.1, 0.9)), mono(32), HUD, 1)
    v = 2887 * prog(t, 0.3, 2.4)
    jit = 2 * math.sin(t * 40) if t < 2.7 else 0
    text_a(img, (80 + jit, 450), f"${v/1000:.2f}", dfont("Black", 260), WHITE, prog(t, 0.2, 0.4))
    p = back((t - 0.6) / 0.5); text_a(img, (80, 730), "TRILLION", dfont("Black", 120), RED, clamp((t - 0.6) / 0.3))
    rect_a(img, (80, 880, 80 + int(920 * prog(t, 0.8, 1.2)), 884), RED)
    items = [("RECORD", "highest level SIPRI has ever recorded"), ("11 YEARS", "of growth in a row"), ("58%", "spent by just 5 countries")]
    for i, (k, s) in enumerate(items):
        y = 960 + i * 190; st = 2.2 + i * 1.2; a = clamp((t - st) / 0.3); dx = (1 - back((t - st) / 0.5)) * -120
        rect_a(img, (80 + dx, y, 1000 + dx, y + 150), (14, 22, 22), a * 0.85, 14, HUD, 2)
        rect_a(img, (80 + dx, y, 92 + dx, y + 150), AMBER, a)
        text_a(img, (120 + dx, y + 18), k, dfont("Black", 64), WHITE, a)
        text_a(img, (120 + dx, y + 96), s, font("Medium", 38), MUTED, a)

C = [
 (1, "US", "UNITED STATES", 954, "3.1%", "Spending dipped", AMBER, ["More than the next six", "countries combined"]),
 (2, "CN", "CHINA", 336, "1.7%", "+7.4% in a year", RED, ["31st straight year", "of increases"]),
 (3, "RU", "RUSSIA", 190, "7.5%", "Record share of budget", RED, ["Military's share of state spending", "at its highest ever"]),
 (4, "DE", "GERMANY", 114, "2.3%", "#4 arms exporter", RED, ["Overtook China in global", "arms exports"]),
 (5, "IN", "INDIA", 92, "2.3%", "+8.9% in a year", RED, ["Holds its spot as the world's", "5th-largest military spender"]),
 (6, "GB", "UNITED KINGDOM", 89, "2.4%", "-2.0% in a year", GREEN, ["One of the few big spenders", "that cut its budget"]),
 (7, "UA", "UKRAINE", 84, "39.6%", "Highest burden", RED, ["Nearly 40% of its entire", "economy goes to defence"]),
 (8, "SA", "SAUDI ARABIA", 83, "6.5%", "+1.4% in a year", RED, ["Spends 6.5% of its economy", "on the military"]),
]

def country_scene(idx):
    rank, code, name, val, gdp, chg, chgcol, fact = C[idx]
    def s(img, t, D, tg):
        fx, fy, fw = W - 80 - 400, 380, 400; fh = int(fw * 128 / 136)
        radar(img, fx + fw / 2, fy + fh / 2 + 10, 300, tg, 0.6 * prog(t, 0, 0.5), speed=140)
        chrome(img, tg)
        for i in range(8):
            rect_a(img, (80 + i * 46, 310, 80 + i * 46 + (34 if i == idx else 22), 318), RED if i == idx else (50, 62, 66), 1, 4)
        p = back((t - 0.05) / 0.5)
        text_a(img, (80, 380), f"#{rank}", dfont("Black", 150 + int(30 * (1 - p))), RED, clamp(t / 0.25))
        text_a(img, (84, 560), typed("TOP MILITARY SPENDER", prog(t, 0.2, 0.6)), mono(28), HUD, 1)
        # flag with lock-on brackets and scan line
        fa = clamp((t - 0.15) / 0.3); bob = 6 * math.sin(tg * 2.2)
        paste_a(img, flag(code, fw), (fx, fy + bob), fa)
        lk = ease((t - 0.3) / 0.6); pad = 20 + 90 * (1 - lk)
        brackets(img, (fx - pad, fy - pad + bob, fx + fw + pad, fy + fh + pad + bob), RED if lk < 1 else HUD, clamp((t - 0.3) / 0.2), 44, 5)
        if 0.3 < t < 1.6:
            sy = fy + fh * ((t - 0.3) / 1.3); rect_a(img, (fx - 10, sy, fx + fw + 10, sy + 4), HUD, 0.8)
        if lk >= 1:
            text_a(img, (fx + fw / 2, fy - 50), "● PROFILE LOADED", mono(24), HUD, clamp((t - 0.9) / 0.3), "mm")
        # typed name with cursor
        size = 110 if len(name) <= 10 else 84
        nm = typed(name, prog(t, 0.4, 0.7))
        text_a(img, (80, 760), nm, dfont("Black", size), WHITE, 1)
        if (len(nm) < len(name) or int(tg * 3) % 2 == 0) and 0.4 < t < 3:
            cx = 80 + ImageDraw.Draw(img).textlength(nm, font=dfont("Black", size)) + 10
            rect_a(img, (cx, 770, cx + 22, 770 + int(size * 0.75)), HUD, 1)
        g = prog(t, 0.6, 1.8)
        text_a(img, (80, 900), f"${int(round(val * g))}", dfont("Black", 230), WHITE, clamp((t - 0.6) / 0.3))
        text_a(img, (80, 1150), "BILLION / YEAR", dfont("Black", 64), RED, clamp((t - 0.8) / 0.3))
        ba = clamp((t - 1.0) / 0.3); bw = 920
        rect_a(img, (80, 1255, 80 + bw, 1277), (24, 34, 36), ba, 8)
        segs = int(46 * val / 954 * prog(t, 1.0, 1.5))
        for k in range(segs):
            rect_a(img, (80 + k * 20, 1257, 80 + k * 20 + 15, 1275), RED, ba, 2)
        text_a(img, (80, 1300), "Scale: United States = full bar", font("Regular", 28), MUTED, ba)
        for j, (lab, v, col) in enumerate([("OF GDP", gdp, WHITE), ("ARMS EXPORTS" if code == "DE" else "2025 TREND", chg, chgcol)]):
            st = 1.5 + j * 0.25; ca = clamp((t - st) / 0.25); dy = (1 - back((t - st) / 0.5)) * 50; x = 80 + j * 470
            rect_a(img, (x, 1370 + dy, x + 440, 1520 + dy), (14, 22, 24), ca * 0.9, 18, HUD if j == 0 else col, 2)
            text_a(img, (x + 30, 1395 + dy), lab, mono(24), MUTED, ca)
            vf = dfont("Black", 60) if len(v) < 9 else dfont("Bold", 40)
            text_a(img, (x + 30, 1440 + dy), v, vf, col, ca)
        text_a(img, (80, 1560), typed(fact[0], prog(t, 2.1, 0.8)), font("SemiBold", 42), AMBER, 1)
        text_a(img, (80, 1612), typed(fact[1], prog(t, 2.7, 0.8)), font("SemiBold", 42), AMBER, 1)
    return s

GDP = [("UA", "Ukraine", 39.6), ("DZ", "Algeria", 8.8), ("IL", "Israel", 7.8), ("RU", "Russia", 7.5)]
def s_burden(img, t, D, tg):
    radar(img, W - 60, 1100, 460, tg, 0.4 * prog(t, 0, 0.6))
    chrome(img, tg)
    text_a(img, (80, 330), "BIGGEST BURDEN", dfont("Black", 90), WHITE, clamp(t / 0.3))
    text_a(img, (80, 440), typed("> military spending as a share of GDP", prog(t, 0.2, 1.0)), mono(28), HUD, 1)
    for i, (code, name, pct) in enumerate(GDP):
        st = 0.6 + i * 1.2; a = clamp((t - st) / 0.25); dx = (1 - back((t - st) / 0.5)) * 140; y = 540 + i * 245
        rect_a(img, (60, y - 10, W - 60, y + 200), (14, 22, 24), a * 0.7, 18, RED if i == 0 else None, 2)
        paste_a(img, flag(code, 150), (90 + dx, y + 30), a)
        v = pct * prog(t, st, 1.2)
        text_a(img, (280 + dx, y + 10), f"{v:.1f}%", dfont("Black", 130), RED if i == 0 else WHITE, a)
        text_a(img, (W - 90, y + 95), name, font("SemiBold", 48), WHITE, a, "rm")
    text_a(img, (80, 1560), "World average: 2.5% of GDP", font("SemiBold", 46), AMBER, clamp((t - 5.4) / 0.4))

def s_outro(img, t, D, tg):
    radar(img, W / 2, 1050, 520, tg, 0.45 * prog(t, 0, 0.6))
    chrome(img, tg)
    text_a(img, (80, 380), typed("> REGIONAL TREND, 2025", prog(t, 0, 0.8)), mono(32), HUD, 1)
    for i, (r, p) in enumerate([("Europe", "+14%"), ("Africa", "+8.5%"), ("Asia & Oceania", "+8.1%")]):
        st = 0.4 + i * 0.5; a = clamp((t - st) / 0.25); dx = (1 - back((t - st) / 0.5)) * 140; y = 470 + i * 170
        rect_a(img, (60, y - 15, W - 60, y + 120), (14, 22, 24), a * 0.8, 16, HUD, 2)
        text_a(img, (100 + dx, y + 52), r, font("SemiBold", 60), WHITE, a, "lm")
        text_a(img, (W - 100, y + 52), p, dfont("Black", 72), RED, a, "rm")
    text_a(img, (80, 1100), typed("The world is spending more", prog(t, 2.4, 1.0)), dfont("Bold", 64), WHITE, 1)
    text_a(img, (80, 1185), typed("on its militaries than ever.", prog(t, 3.4, 1.0)), dfont("Bold", 64), WHITE, 1)
    p = back((t - 5.2) / 0.5)
    rect_a(img, (80, 1330, 80 + int(560 * clamp(p, 0, 1.2)), 1430), RED, clamp((t - 5.2) / 0.2), 50)
    text_a(img, (110, 1380), "FOLLOW FOR MORE  →", font("Bold", 44), WHITE, clamp((t - 5.5) / 0.3), "lm")

FNS = [("00_title", s_title), ("01_global", s_global)] + [(f"{i+2:02d}_{C[i][1]}", country_scene(i)) for i in range(8)] + [("10_burden", s_burden), ("11_outro", s_outro)]
_d = json.load(open("/home/claude/tts/durs.json"))
LEAD, TAIL = 0.3, 0.45
SCENES = [(n, f, round(max(4.5, _d[i] + LEAD + TAIL) * FPS) / FPS) for i, (n, f) in enumerate(FNS)]
STARTS = np.cumsum([0] + [d for _, _, d in SCENES]).tolist()

def frame(fn, t, D, t0, k):
    tg = t0 + t
    ox = 60 + 50 * math.sin(tg * 0.11); oy = 60 + 50 * math.cos(tg * 0.083)
    img = BG_BIG.crop((int(ox), int(oy), int(ox) + W, int(oy) + H))
    d = ImageDraw.Draw(img)
    for (x, y0, sp, s, a) in PART:
        y = (y0 - sp * tg) % H; xx = x + 12 * math.sin(tg * 0.5 + y0)
        c = tuple(int(BG[i] + (v - BG[i]) * a) for i, v in enumerate((200, 120, 80)))
        d.ellipse([xx - s, y - s, xx + s, y + s], fill=c + (255,))
    fn(img, t, D, tg)
    arr = np.asarray(img.convert("RGB")).copy()
    # glitch transition in/out
    g = max(0.0, 1 - t / 0.22) if t0 > 0 else 0.0
    g = max(g, max(0.0, 1 - (D - t) / 0.12)) if D - t < 0.12 and t0 + D < STARTS[-1] - 0.01 else g
    if g > 0:
        r = np.random.default_rng(k + int(t0 * 1000))
        for _ in range(int(10 * g) + 2):
            y = int(r.uniform(0, H)); h = int(r.uniform(10, 120)); sh = int(r.uniform(-80, 80) * g)
            arr[y:y + h] = np.roll(arr[y:y + h], sh, axis=1)
        arr[..., 0] = np.roll(arr[..., 0], int(14 * g), axis=1)
        arr[..., 2] = np.roll(arr[..., 2], -int(14 * g), axis=1)
        if t < 0.05 and t0 > 0: arr = np.clip(arr.astype(np.int16) + 70, 0, 255).astype(np.uint8)
    if t0 == 0 and t < 0.3: arr = (arr * (t / 0.3)).astype(np.uint8)
    if t0 + D >= STARTS[-1] - 0.01 and D - t < 0.4: arr = (arr * ((D - t) / 0.4)).astype(np.uint8)
    return arr

def render(i):
    name, fn, D = SCENES[i]; t0 = STARTS[i]
    tmp, final = f"out3/{name}.tmp.mp4", f"out3/{name}.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
        "-crf", "17", "-pix_fmt", "yuv420p", "-profile:v", "high", tmp], stdin=subprocess.PIPE)
    for k in range(int(round(D * FPS))):
        p.stdin.write(frame(fn, k / FPS, D, t0, k).tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, final)
    return name

if __name__ == "__main__":
    os.makedirs("out3", exist_ok=True)
    if sys.argv[1] == "still":
        for i, (name, fn, D) in enumerate(SCENES):
            for tt in [float(x) for x in sys.argv[2:]] or [D - 0.5]:
                Image.fromarray(frame(fn, min(tt, D - 0.2), D, STARTS[i], 0)).save(f"out3/still_{name}_{tt}.png")
    elif sys.argv[1] == "full":
        with Pool(2) as p: list(p.imap_unordered(render, sorted(range(len(SCENES)), key=lambda i: -SCENES[i][2])))
        with open("out3/list.txt", "w") as fl:
            for name, _, _ in SCENES: fl.write(f"file '{name}.mp4'\n")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", "out3/list.txt",
                        "-c", "copy", "out3/video_only.mp4"], check=True)
