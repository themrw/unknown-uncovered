#!/usr/bin/env python3
"""Animated cartoon film scenes (16:9) for Unknown Uncovered: puppet characters that walk, talk, blink and gesture,
in painted, animated sets. Illustrations, not likenesses.

usage: uu_toon.py spec.json still t1,t2 | full     (spec "format": "long"; scenes of type "toon" plus any uu_long type)

toon scene: {set, place, title[2], line, cast[{who, x0, x1, walk[t0,t1], pose, face}], <set-specific *_at keys>}
  who: haque | bose | henry | student | clerk | suspect | judge       pose: down | point | card | hold | books | tap | measure | file
  sets: street office measure river college drawers committee writers teagarden court telegraph london credit finale
"""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import uu_long as L, uu_story as S
R = L.R
from uu_render import W, H, T, F, WHITE, MUTED, clamp, ease, back, prog, text_a, rect_a, paste_a, typed, fit_font

INK = (28, 22, 18, 255)
SK = {"haque": (176, 120, 82), "bose": (160, 106, 72), "student": (176, 120, 82), "henry": (232, 190, 160), "clerk": (170, 116, 80),
      "suspect": (40, 34, 34), "judge": (232, 190, 160)}
OUT = {"haque": ((196, 168, 110), (150, 124, 78)), "bose": ((190, 162, 104), (146, 120, 74)), "student": ((240, 236, 222), (196, 190, 170)),
       "henry": ((236, 234, 224), (190, 186, 172)), "clerk": ((70, 66, 70), (46, 44, 48)), "suspect": ((40, 34, 34), (30, 26, 26)),
       "judge": ((140, 30, 34), (100, 20, 24))}
PANT = {"haque": (120, 98, 60), "bose": (116, 94, 58), "student": (236, 232, 218), "henry": (226, 222, 210), "clerk": (50, 48, 52),
        "suspect": (40, 34, 34), "judge": (60, 40, 40)}

def dk(c, f=0.75): return tuple(int(v * f) for v in c[:3]) + (255,)
def rgba(c): return tuple(c[:3]) + (255,)

# ---------------------------------------------------------------- character puppet
def person(who, tg, walk_ph=None, talk=False, pose="down", blink_seed=0.0):
    """RGBA 420x880 image, feet at bottom centre, facing right. walk_ph: walking phase (radians) or None."""
    K = 2; Wd, Hd = 420, 880; im = Image.new("RGBA", (Wd * K, Hd * K), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    def P(pts, fill, ow=5): d.polygon([(x * K, y * K) for x, y in pts], fill=fill, outline=INK, width=ow * K // 2)
    def E(b, fill, ow=5): d.ellipse([v * K for v in b], fill=fill, outline=INK, width=ow * K // 2)
    def Ln(pts, fill=INK, w=5): d.line([(x * K, y * K) for x, y in pts], fill=fill, width=int(w * K), joint="curve")
    sil = who == "suspect"
    skin = rgba(SK[who]); skd = dk(SK[who], 0.8); cloth, clothd = rgba(OUT[who][0]), rgba(OUT[who][1]); pant = rgba(PANT[who])
    cx = 210; foot = 860; hip = 540; sh = 300; hy = 190; bob = 0
    if walk_ph is not None: bob = -6 * abs(math.sin(walk_ph))
    hip += bob; sh += bob; hy += bob
    # legs
    for side, sgn in ((0, 1), (1, -1)):
        a = math.radians(90 + (22 * math.sin(walk_ph) * sgn if walk_ph is not None else (3 if side else -3)))
        kx, ky = cx + (side - 0.5) * 44 + math.cos(a) * 160, hip + math.sin(a) * 160
        a2 = a + (math.radians(max(0, 25 * math.sin(walk_ph + (0 if side else math.pi)))) if walk_ph is not None else 0)
        fx, fy = kx + math.cos(a2) * 150, min(foot - 10, ky + math.sin(a2) * 150)
        col = pant if side == 0 else dk(PANT[who], 0.85)
        Ln([(cx + (side - 0.5) * 44, hip), (kx, ky), (fx, fy)], INK, 64); Ln([(cx + (side - 0.5) * 44, hip), (kx, ky), (fx, fy)], col, 56)
        E([fx - 32, fy - 8, fx + 50, fy + 24], (30, 24, 20, 255), 4)
    # back arm (behind torso)
    arms = {"down": ((96, 92), (84, 88)), "point": ((96, 92), (-8, -4)), "card": ((96, 92), (55, -55)), "hold": ((96, 92), (60, -40)),
            "books": ((70, -20), (66, -24)), "tap": ((96, 92), (40, 60)), "measure": ((20, -10), (30, 0)), "file": ((96, 92), (88, 60))}
    (ba1, ba2), (fa1, fa2) = arms.get(pose, arms["down"])
    if walk_ph is not None and pose in ("down", "file"):
        ba1 = 92 - 18 * math.sin(walk_ph); ba2 = ba1 - 8; fa1 = 92 + 18 * math.sin(walk_ph); fa2 = fa1 - 10 if pose == "down" else fa1 - 30
    def arm(sx, a1, a2, col, front):
        ax, ay = cx + sx, sh + 18
        ex, ey = ax + math.cos(math.radians(a1)) * 120, ay + math.sin(math.radians(a1)) * 120
        hx, hy_ = ex + math.cos(math.radians(a2)) * 110, ey + math.sin(math.radians(a2)) * 110
        Ln([(ax, ay), (ex, ey), (hx, hy_)], INK, 50); Ln([(ax, ay), (ex, ey), (hx, hy_)], col, 42)
        E([hx - 20, hy_ - 20, hx + 20, hy_ + 20], skin if not sil else clothd, 4)
        return hx, hy_
    arm(-74, 180 - ba1 if pose in ("measure",) else ba1, 180 - ba2 if pose in ("measure",) else ba2, clothd, False)
    # torso
    P([(cx - 90, sh + 6), (cx - 70, sh - 8), (cx + 70, sh - 8), (cx + 90, sh + 6), (cx + 84, hip + 14), (cx - 84, hip + 14)], cloth)
    P([(cx + 34, sh - 4), (cx + 70, sh - 8), (cx + 90, sh + 6), (cx + 84, hip + 14), (cx + 44, hip + 14)], clothd, 0)
    if who in ("haque", "bose"):
        P([(cx - 85, hip - 46), (cx + 85, hip - 46), (cx + 86, hip - 26), (cx - 86, hip - 26)], (110, 70, 32, 255), 3)
        E([cx - 14, hip - 48, cx + 14, hip - 24], (226, 186, 90, 255), 3)
        for k in range(4): E([cx - 6, sh + 30 + k * 40, cx + 6, sh + 42 + k * 40], (226, 186, 90, 255), 2)
        P([(cx - 30, sh), (cx + 30, sh), (cx + 16, sh + 26), (cx - 16, sh + 26)], clothd, 3)
    if who == "henry":
        for k in range(4): E([cx - 6, sh + 30 + k * 40, cx + 6, sh + 42 + k * 40], (210, 180, 90, 255), 2)
        P([(cx - 70, sh + 4), (cx - 40, sh + 4), (cx - 46, sh + 22), (cx - 70, sh + 22)], (60, 70, 120, 255), 2)
    if who == "student":
        Ln([(cx - 40, sh + 8), (cx + 50, hip - 60)], (200, 60, 50, 255), 10)
    if who == "judge":
        P([(cx - 26, sh), (cx + 26, sh), (cx + 10, sh + 40), (cx - 10, sh + 40)], (245, 245, 240, 255), 3)
    if who == "clerk":
        P([(cx - 22, sh), (cx + 22, sh), (cx, sh + 60)], (236, 232, 222, 255), 2); Ln([(cx, sh + 6), (cx, sh + 58)], (140, 30, 30, 255), 6)
    # neck + head
    E([cx - 22, hy + 60, cx + 22, sh + 20], skin if not sil else cloth, 4)
    E([cx - 74, hy - 84, cx + 70, hy + 100], skin if not sil else cloth, 5)
    if not sil:
        d.chord([(cx + 14) * K, (hy - 80) * K, (cx + 68) * K, (hy + 96) * K], 270, 90, fill=skd)
        E([cx + 44, hy + 30, cx + 64, hy + 44], (205, 120, 100, 120), 0)
        E([cx - 86, hy - 6, cx - 64, hy + 34], skin, 4)                                         # ear
        bl = ((tg + blink_seed) % 3.3) < 0.12
        for ex in (cx + 4, cx + 40):
            if bl: Ln([(ex - 10, hy + 6), (ex + 10, hy + 6)], INK, 4)
            else:
                E([ex - 11, hy - 4, ex + 11, hy + 14], (250, 248, 240, 255), 3); E([ex - 3, hy, ex + 7, hy + 12], (40, 28, 20, 255), 0)
            Ln([(ex - 14, hy - 16), (ex + 12, hy - 18)], (40, 30, 24, 255), 5)
        if who in ("haque", "student"):
            for ex in (cx + 4, cx + 40): d.ellipse([(ex - 15) * K, (hy - 8) * K, (ex + 15) * K, (hy + 20) * K], outline=(60, 44, 30, 255), width=2 * K)
            Ln([(cx + 20, hy + 4), (cx + 24, hy + 4)], (40, 30, 20, 255), 3)
        Ln([(cx + 30, hy + 14), (cx + 40, hy + 40), (cx + 28, hy + 44)], dk(SK[who], 0.6), 4)    # nose
        mo = talk and int(tg * 9) % 3 != 0
        if who in ("bose", "henry"): P([(cx + 8, hy + 50), (cx + 26, hy + 44), (cx + 50, hy + 52), (cx + 52, hy + 62), (cx + 28, hy + 56), (cx + 8, hy + 62)], (40, 32, 28, 255), 2)
        if who in ("haque", "judge", "clerk"): Ln([(cx + 14, hy + 52), (cx + 48, hy + 52)], (40, 32, 28, 255), 4)
        if mo: E([cx + 20, hy + 60, cx + 44, hy + 76], (90, 30, 30, 255), 3)
        else: Ln([(cx + 20, hy + 66), (cx + 44, hy + 64)], INK, 4)
    # headwear / hair
    if who in ("haque", "bose"):
        E([cx - 80, hy - 124, cx + 76, hy - 18], (178, 38, 44, 255), 5)
        for k in range(3): d.arc([(cx - 64) * K, (hy - (98 - k * 22)) * K, (cx + 60) * K, (hy - (40 - k * 22)) * K], 200, 340, fill=(120, 22, 28, 255), width=4 * K)
        E([cx + 20, hy - 70, cx + 40, hy - 50], (226, 186, 90, 255), 3)
    elif who == "henry":
        E([cx - 92, hy - 52, cx + 92, hy - 30], (244, 240, 228, 255), 4); E([cx - 66, hy - 128, cx + 64, hy - 34], (248, 244, 232, 255), 5)
        Ln([(cx - 66, hy - 60), (cx + 64, hy - 60)], (170, 150, 110, 255), 6)
    elif who == "judge":
        for k in range(5): E([cx - 74 + k * 30, hy - 80, cx - 34 + k * 30, hy - 30], (236, 236, 232, 255), 3)
        for sx in (-1, 1): E([cx - 4 + sx * 70 - 22, hy - 20, cx - 4 + sx * 70 + 22, hy + 70], (236, 236, 232, 255), 3)
    if who in ("haque", "bose", "henry") and not sil:
        P([(cx - 74, hy - 30), (cx - 50, hy - 40), (cx - 46, hy + 30), (cx - 66, hy + 40)], (34, 26, 22, 255), 0)   # hair at the temple
    if who in ("haque", "bose", "henry", "judge", "clerk", "student") and not sil:
        P([(cx - 70, hy - 84 + 20), (cx - 74, hy), (cx - 60, hy - 50)], (34, 26, 22, 0), 0)
    if False:
        pass
    elif who not in ("haque", "bose", "henry", "judge") and not sil:
        P([(cx - 64, hy - 10), (cx - 60, hy - 60), (cx - 20, hy - 76), (cx + 40, hy - 70), (cx + 60, hy - 40), (cx + 58, hy - 20), (cx + 20, hy - 46), (cx - 30, hy - 40)], (34, 26, 22, 255), 3)
    # front arm + props
    if pose == "measure": hx, hy2 = arm(74, 0, -10, cloth, True)
    else: hx, hy2 = arm(74, fa1, fa2, cloth, True)
    if pose in ("card", "hold"):
        P([(hx - 10, hy2 - 74), (hx + 56, hy2 - 80), (hx + 60, hy2 + 4), (hx - 6, hy2 + 10)], (250, 246, 232, 255), 3)
        for k in range(3): d.arc([(hx + 4 + k * 4) * K, (hy2 - 60 + k * 6) * K, (hx + 44 - k * 4) * K, (hy2 - 10 - k * 4) * K], 200, 340, fill=(60, 50, 40, 255), width=2 * K)
    if pose == "books":
        P([(hx - 120, hy2 - 50), (hx + 20, hy2 - 50), (hx + 20, hy2 - 6), (hx - 120, hy2 - 6)], (120, 40, 40, 255), 3)
        P([(hx - 110, hy2 - 80), (hx + 10, hy2 - 80), (hx + 10, hy2 - 50), (hx - 110, hy2 - 50)], (40, 70, 110, 255), 3)
    if pose == "file":
        P([(hx - 30, hy2 - 10), (hx + 50, hy2 - 16), (hx + 54, hy2 + 90), (hx - 26, hy2 + 96)], (196, 160, 90, 255), 3)
    if pose == "measure":
        Ln([(hx, hy2), (hx + 90, hy2 - 30), (hx + 150, hy2 + 20)], (150, 150, 160, 255), 8)
    im = im.resize((Wd, Hd), Image.LANCZOS)
    return im

# ---------------------------------------------------------------- sets (painted once, cached)
_set = {}
def grad(top, bot, h0=0, h1=H):
    y = np.linspace(0, 1, h1 - h0)[:, None, None]
    a = (np.array(top) * (1 - y) + np.array(bot) * y) * np.ones((1, W, 1))
    return Image.fromarray(a.astype(np.uint8)).convert("RGBA")

def glow(img, box, col, a, blur=60):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse(box, fill=col + (int(a),)); img.alpha_composite(g.filter(ImageFilter.GaussianBlur(blur)))

def building_row(d, y0, y1, col, win, rng, arches=True, x0=0, x1=W):
    x = x0
    while x < x1:
        w = rng.randint(220, 380); h = rng.randint(int((y1 - y0) * 0.6), y1 - y0)
        d.rectangle([x, y1 - h, x + w, y1], fill=col)
        d.rectangle([x - 6, y1 - h - 14, x + w + 6, y1 - h], fill=tuple(int(c * 0.8) for c in col[:3]) + (255,))
        for r_ in range(int(h / 110)):
            for c in range(int(w / 80)):
                wx = x + 22 + c * 80; wy = y1 - h + 34 + r_ * 110
                if wy + 70 > y1 - 20: continue
                if arches: d.rounded_rectangle([wx, wy, wx + 40, wy + 64], 20, fill=win)
                else: d.rectangle([wx, wy, wx + 40, wy + 64], fill=win)
        x += w + rng.randint(0, 30)

def paint_set(name):
    rng = random.Random(hash(name) % 1000)
    if name in ("street", "finale"):
        img = grad((250, 170, 90), (255, 214, 150), 0, H) if name == "street" else grad((240, 120, 70), (255, 190, 120))
        glow(img, [1200, 200, 1900, 900], (255, 240, 200), 160, 120)
        d = ImageDraw.Draw(img)
        building_row(d, 300, 900, (196, 120, 90, 255), (90, 60, 50, 255), rng)
        img.alpha_composite(Image.new("RGBA", (W, H), (255, 200, 150, 40)))
        d = ImageDraw.Draw(img); building_row(d, 360, 920, (150, 82, 60, 255), (60, 40, 34, 255), rng)
        d.rectangle([0, 900, W, H], fill=(120, 96, 76, 255)); d.rectangle([0, 900, W, 916], fill=(90, 70, 56, 255))
        for x in (300, 980, 1660):
            d.rectangle([x - 6, 560, x + 6, 910], fill=(30, 30, 34, 255)); d.rectangle([x - 22, 530, x + 22, 570], fill=(30, 30, 34, 255))
            glow(img, [x - 60, 490, x + 60, 610], (255, 220, 140), 200, 30)
    elif name == "office":
        img = grad((70, 52, 40), (40, 30, 24)); d = ImageDraw.Draw(img)
        for s in range(4):
            y = 180 + s * 190; d.rectangle([0, y + 150, 900, y + 166], fill=(80, 50, 30, 255))
            x = 10
            while x < 880:
                w = rng.randint(50, 90); h = rng.randint(80, 150)
                d.rectangle([x, y + 150 - h, x + w, y + 150], fill=(rng.randint(200, 235), rng.randint(185, 215), rng.randint(150, 175), 255), outline=(120, 100, 80, 255))
                d.line([x + w / 2, y + 150 - h, x + w / 2, y + 150], fill=(170, 40, 40, 255), width=3); x += w + 4
        d.rectangle([1200, 160, 1640, 620], fill=(255, 230, 170, 255)); d.line([1420, 160, 1420, 620], fill=(70, 50, 36, 255), width=10)
        d.line([1200, 390, 1640, 390], fill=(70, 50, 36, 255), width=10)
        rays = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(rays).polygon([(1200, 160), (1640, 160), (1300, 1080), (700, 1080)], fill=(255, 220, 150, 60))
        img.alpha_composite(rays.filter(ImageFilter.GaussianBlur(30))); d = ImageDraw.Draw(img)
        d.rectangle([0, 960, W, H], fill=(60, 40, 28, 255))
        d.rectangle([1500, 760, 1900, 800], fill=(90, 56, 32, 255)); d.rectangle([1520, 800, 1540, 970], fill=(70, 44, 26, 255)); d.rectangle([1860, 800, 1880, 970], fill=(70, 44, 26, 255))
        for k in range(6): d.rectangle([1560 + k * 40, 700 - k * 12, 1640 + k * 40, 760], fill=(236, 226, 196, 255), outline=(150, 130, 100, 255))
    elif name == "measure":
        img = grad((60, 56, 64), (30, 28, 34)); d = ImageDraw.Draw(img)
        d.rectangle([680, 140, 900, 960], fill=(220, 212, 190, 255))
        for k in range(40):
            y = 160 + k * 20; d.line([680, y, 680 + (60 if k % 5 == 0 else 30), y], fill=(60, 50, 40, 255), width=3)
            if k % 5 == 0: d.text((750, y - 12), str(200 - k * 5), font=F("mono", 20), fill=(60, 50, 40, 255))
        d.rectangle([0, 960, W, H], fill=(44, 40, 44, 255))
    elif name == "river":
        img = grad((60, 70, 110), (230, 150, 110), 0, H); d = ImageDraw.Draw(img)
        glow(img, [760, 360, 1160, 760], (255, 200, 150), 200, 80); d = ImageDraw.Draw(img)
        d.ellipse([900, 500, 1020, 620], fill=(255, 220, 170, 255))
        for k in range(8): d.polygon([(k * 300 - 100, 640), (k * 300 + 60, 560 - rng.randint(0, 60)), (k * 300 + 220, 640)], fill=(40, 46, 60, 255))
        img.alpha_composite(grad((90, 90, 120), (30, 36, 56), 0, H).crop((0, 0, W, H - 640)).resize((W, H - 640)), (0, 640))
        d = ImageDraw.Draw(img)
        d.polygon([(0, 1080), (0, 860), (380, 840), (620, 1080)], fill=(24, 28, 30, 255))
        for k in range(7):
            x = 40 + k * 70; d.line([x, 860, x - 10 + k * 3, 760 - k * 6], fill=(30, 40, 30, 255), width=4)
    elif name == "college":
        img = grad((150, 190, 230), (230, 230, 220)); d = ImageDraw.Draw(img)
        d.rectangle([260, 260, 1660, 900], fill=(232, 222, 196, 255)); d.polygon([(220, 260), (960, 120), (1700, 260)], fill=(222, 210, 182, 255), outline=(170, 150, 120, 255))
        for k in range(10):
            x = 330 + k * 140; d.rectangle([x, 300, x + 46, 860], fill=(244, 238, 222, 255), outline=(190, 176, 150, 255))
            d.rectangle([x - 8, 292, x + 54, 312], fill=(210, 198, 172, 255))
        for k in range(4): d.rectangle([200 - k * 30, 860 + k * 30, 1720 + k * 30, 890 + k * 30], fill=(210, 200, 180, 255), outline=(170, 160, 140, 255))
        for x in (80, 1840):
            d.ellipse([x - 140, 300, x + 140, 640], fill=(60, 110, 60, 255)); d.rectangle([x - 14, 600, x + 14, 960], fill=(80, 60, 40, 255))
        d.rectangle([0, 980, W, H], fill=(150, 140, 120, 255))
        d.text((960, 220), "PRESIDENCY COLLEGE", font=F("disp", 40, "Black"), fill=(120, 100, 70, 255), anchor="mm")
    elif name == "drawers":
        img = grad((40, 34, 30), (22, 18, 16)); d = ImageDraw.Draw(img)
        x0, y0, s = 760, 120, 26
        for r_ in range(32):
            for c in range(32):
                x = x0 + c * s; y = y0 + r_ * s
                d.rectangle([x, y, x + s - 3, y + s - 3], fill=(96, 62, 36, 255), outline=(60, 38, 22, 255))
                d.rectangle([x + 9, y + 10, x + 15, y + 13], fill=(210, 170, 90, 255))
        d.rectangle([0, 980, W, H], fill=(50, 34, 24, 255))
        d.rectangle([180, 820, 700, 860], fill=(90, 56, 32, 255))
    elif name == "committee":
        img = grad((60, 46, 36), (30, 24, 20)); d = ImageDraw.Draw(img)
        for k in range(3): d.rectangle([200 + k * 560, 120, 540 + k * 560, 520], fill=(80, 60, 44, 255), outline=(120, 92, 64, 255), width=6)
        d.polygon([(100, 760), (1820, 760), (1900, 980), (20, 980)], fill=(90, 56, 32, 255))
        for k in range(7):
            x = 260 + k * 230; d.ellipse([x - 40, 560, x + 40, 650], fill=(30, 26, 26, 255)); d.rounded_rectangle([x - 70, 640, x + 70, 790], 30, fill=(30, 26, 26, 255))
        for k in range(6): d.rectangle([300 + k * 240, 740, 380 + k * 240, 760], fill=(236, 226, 196, 255))
    elif name == "writers":
        img = grad((140, 180, 220), (220, 220, 210)); d = ImageDraw.Draw(img)
        d.rectangle([0, 200, W, 900], fill=(170, 60, 40, 255)); d.rectangle([0, 190, W, 220], fill=(140, 46, 30, 255))
        for k in range(14):
            x = 40 + k * 136
            for r_ in range(3): d.rounded_rectangle([x, 250 + r_ * 210, x + 70, 400 + r_ * 210], 34, fill=(70, 30, 24, 255), outline=(230, 210, 180, 255), width=4)
            d.rectangle([x + 90, 220, x + 110, 900], fill=(220, 200, 170, 255))
        d.polygon([(760, 190), (960, 80), (1160, 190)], fill=(150, 50, 34, 255)); d.rectangle([780, 120, 1140, 190], fill=(160, 54, 36, 255))
        d.rectangle([0, 900, W, H], fill=(150, 140, 120, 255))
        d.rounded_rectangle([740, 118, 1180, 178], 10, fill=(30, 40, 30, 255), outline=(220, 190, 110, 255), width=4)
        d.text((960, 148), "FINGER PRINT BUREAU · 1897", font=F("disp", 26, "Black"), fill=(240, 220, 160, 255), anchor="mm")
    elif name == "teagarden":
        img = grad((12, 16, 34), (30, 40, 50)); d = ImageDraw.Draw(img)
        for k in range(160):
            x, y = rng.randint(0, W), rng.randint(0, 380); d.ellipse([x, y, x + 3, y + 3], fill=(230, 230, 250, rng.randint(80, 220)))
        d.ellipse([1500, 90, 1600, 190], fill=(240, 240, 220, 255))
        for k in range(6):
            yb = 520 + k * 90; pts = [(x, yb - 40 * math.sin(x / 260 + k)) for x in range(0, W + 40, 40)]
            d.polygon(pts + [(W, H), (0, H)], fill=(20 + k * 6, 46 + k * 10, 30 + k * 4, 255))
            for x in range(0, W, 60): d.ellipse([x, yb - 40 * math.sin(x / 260 + k) - 18, x + 56, yb - 40 * math.sin(x / 260 + k) + 14], fill=(30 + k * 8, 70 + k * 12, 40 + k * 4, 255))
        d.polygon([(300, 560), (520, 440), (740, 560)], fill=(60, 40, 34, 255)); d.rectangle([340, 560, 700, 760], fill=(110, 90, 70, 255))
        d.rectangle([420, 610, 500, 690], fill=(255, 200, 110, 255)); d.rectangle([560, 610, 640, 690], fill=(255, 200, 110, 255))
        glow(img, [380, 580, 680, 720], (255, 190, 90), 160, 40)
    elif name == "court":
        img = grad((70, 46, 30), (40, 26, 18)); d = ImageDraw.Draw(img)
        for k in range(8): d.rectangle([k * 250, 0, k * 250 + 230, 700], fill=(86, 56, 36, 255), outline=(60, 38, 24, 255), width=6)
        d.rectangle([1100, 620, 1760, 980], fill=(96, 60, 36, 255), outline=(60, 38, 24, 255), width=8)
        d.ellipse([1360, 180, 1500, 320], fill=(180, 150, 80, 255), outline=(110, 90, 40, 255), width=6)
        d.rectangle([0, 980, W, H], fill=(50, 32, 22, 255))
    elif name == "telegraph":
        img = grad((50, 44, 40), (26, 22, 20)); d = ImageDraw.Draw(img)
        d.rectangle([1300, 140, 1800, 560], fill=(150, 170, 190, 255)); d.line([1550, 140, 1550, 560], fill=(60, 50, 40, 255), width=8)
        for k in range(4): d.line([1300, 560 - k * 4, 0 + k * 3, 120 + k * 60], fill=(30, 30, 30, 255), width=3)
        d.rectangle([600, 760, 1300, 800], fill=(90, 56, 32, 255)); d.rectangle([620, 800, 640, 980], fill=(70, 44, 26, 255)); d.rectangle([1260, 800, 1280, 980], fill=(70, 44, 26, 255))
        d.rectangle([880, 730, 1040, 760], fill=(60, 50, 40, 255)); d.rectangle([1080, 700, 1220, 760], fill=(160, 120, 50, 255))
        d.rectangle([0, 980, W, H], fill=(44, 32, 26, 255))
    elif name == "london":
        img = grad((70, 80, 96), (130, 130, 130)); d = ImageDraw.Draw(img)
        d.rectangle([1300, 160, 1420, 800], fill=(50, 54, 62, 255)); d.polygon([(1300, 160), (1360, 40), (1420, 160)], fill=(50, 54, 62, 255))
        d.ellipse([1320, 210, 1400, 290], fill=(230, 220, 170, 255), outline=(40, 40, 40, 255), width=4)
        building_row(d, 360, 800, (70, 74, 82, 255), (200, 180, 120, 255), rng, arches=False, x0=0, x1=1280)
        building_row(d, 400, 800, (64, 68, 76, 255), (200, 180, 120, 255), rng, arches=False, x0=1440, x1=W)
        d.rectangle([0, 800, W, 900], fill=(60, 66, 74, 255)); d.rectangle([0, 900, W, H], fill=(90, 90, 92, 255))
        d.rounded_rectangle([200, 600, 640, 680], 8, fill=(30, 40, 70, 255), outline=(220, 220, 230, 255), width=4)
        d.text((420, 640), "SCOTLAND YARD", font=F("disp", 36, "Black"), fill=(240, 240, 250, 255), anchor="mm")
    elif name == "credit":
        img = grad((24, 18, 14), (10, 8, 6)); glow(img, [500, 200, 1420, 900], (255, 190, 90), 120, 140)
    else:
        img = grad((30, 30, 30), (10, 10, 10))
    return img

def get_set(name):
    if name not in _set: _set[name] = paint_set(name)
    return _set[name]

# ---------------------------------------------------------------- per-frame set animation
def set_fx(img, name, sc, t, D, tg):
    d = ImageDraw.Draw(img)
    if name in ("street", "finale"):
        x = (tg * 140) % (W + 600) - 300; y = 880                                  # horse carriage crossing
        d.ellipse([x - 160, y - 150, x - 40, y - 60], fill=(60, 40, 30, 255)); d.rectangle([x - 120, y - 120, x - 40, y - 40], fill=(60, 40, 30, 255))
        for lx in (-150, -70): d.line([x + lx, y - 50, x + lx + 8 * math.sin(tg * 8 + lx), y], fill=(50, 34, 26, 255), width=8)
        d.rounded_rectangle([x, y - 170, x + 200, y - 50], 18, fill=(70, 30, 24, 255)); d.rectangle([x + 30, y - 150, x + 90, y - 100], fill=(240, 210, 150, 255))
        for wx in (x + 40, x + 170):
            d.ellipse([wx - 40, y - 80, wx + 40, y], outline=(40, 30, 24, 255), width=8)
            a = tg * 5; d.line([wx - 34 * math.cos(a), y - 40 - 34 * math.sin(a), wx + 34 * math.cos(a), y - 40 + 34 * math.sin(a)], fill=(40, 30, 24, 255), width=4)
        for k in range(5):
            bx = (tg * 60 + k * 400) % (W + 200) - 100; by = 160 + 40 * math.sin(k * 3) + 10 * math.sin(tg * 6 + k)
            d.line([bx - 16, by, bx, by + 8 * math.sin(tg * 10 + k), bx + 16, by], fill=(60, 40, 40, 255), width=3)
    if name == "office":                                                           # ceiling fan
        cx, cy = 960, 80; d.line([cx, 0, cx, cy], fill=(40, 30, 24, 255), width=8)
        for k in range(3):
            a = tg * 3 + k * 2.09; d.ellipse([cx + 260 * math.cos(a) - 70, cy + 30 * math.sin(a) - 12, cx + 260 * math.cos(a) + 70, cy + 30 * math.sin(a) + 12], fill=(70, 50, 36, 255))
        d.ellipse([cx - 30, cy - 18, cx + 30, cy + 18], fill=(40, 30, 24, 255))
        for k in range(10):
            ph = (tg * 0.1 + k * 0.13) % 1; x = 800 + k * 80 + 30 * math.sin(tg + k); y = 200 + ph * 760
            d.ellipse([x, y, x + 4, y + 4], fill=(255, 230, 180, int(140 * math.sin(ph * math.pi))))
    if name == "measure":
        pa = sc.get("panel_at", [D * 0.2, D * 0.45, D * 0.6])
        for i, (country, sub, icon) in enumerate(sc.get("panels", [])):
            q = clamp((t - pa[i]) / 0.5)
            if q <= 0: continue
            x = 1000 + i * 300; y = 260 + (1 - back(q)) * 80
            rect_a(img, (x, y, x + 270, y + 400), (20, 18, 16), 0.9 * q, 18, T["accent"], 3)
            text_a(img, (x + 135, y + 300), country, F("anton", 50), WHITE, q, "mm"); text_a(img, (x + 135, y + 356), sub, fit_font("inter", 22, sub, 226, "SemiBold"), MUTED, q, "mm")
            d = ImageDraw.Draw(img)
            if icon == "calipers": d.line([x + 70, y + 200, x + 135, y + 70, x + 200, y + 200], fill=(200, 200, 210, int(255 * q)), width=10)
            if icon == "book": d.rectangle([x + 80, y + 60, x + 190, y + 210], fill=(110, 40, 40, int(255 * q))); d.text((x + 135, y + 135), "FINGER\nPRINTS", font=F("disp", 20, "Black"), fill=(240, 220, 160, int(255 * q)), anchor="mm", align="center")
            if icon == "card": img.alpha_composite(S.fp_img(120, 150, 3, (230, 220, 200), 0.9 * q), (int(x + 75), int(y + 60)))
            if t > pa[min(2, len(pa) - 1)] + 2.5 and i == 0: text_a(img, (x + 135, y + 30), "SLOW", F("anton", 36), T["alert"], clamp((t - pa[2] - 2.5) / 0.4), "mm")
    if name == "river":
        bx = 900 + 220 * math.sin(tg * 0.15); by = 820
        d.polygon([(bx - 120, by), (bx + 120, by), (bx + 90, by + 30), (bx - 90, by + 30)], fill=(20, 18, 22, 255)); d.line([bx, by, bx, by - 140], fill=(20, 18, 22, 255), width=5)
        d.polygon([(bx + 4, by - 136), (bx + 90, by - 30), (bx + 4, by - 30)], fill=(60, 56, 64, 255))
        for k in range(12):
            y = 700 + k * 30; x = (tg * (20 + k * 6) + k * 170) % W; d.line([x, y, x + 60 + k * 6, y], fill=(255, 210, 170, 90), width=3)
        d.ellipse([268, 760, 312, 806], fill=(16, 16, 18, 255)); d.polygon([(250, 860), (330, 860), (318, 800), (262, 800)], fill=(16, 16, 18, 255))   # the boy
    if name == "drawers":
        x0, y0, s = 760, 120, 26
        for k in range(3):                                                      # cards flying into drawers
            ph = (tg * 0.5 + k / 3) % 1; tx, ty = x0 + ((k * 11 + int(tg * 0.5)) % 32) * s + 13, y0 + ((k * 7 + int(tg * 0.5) * 3) % 32) * s + 13
            sx, sy = 640, 760; x = sx + (tx - sx) * ph; y = sy + (ty - sy) * ph - 160 * math.sin(ph * math.pi)
            rect_a(img, (x - 24 * (1 - ph) - 6, y - 16 * (1 - ph) - 4, x + 24 * (1 - ph) + 6, y + 16 * (1 - ph) + 4), (250, 246, 232), 1 - ph * 0.6, 3)
        da = sc.get("drawer_at", D * 0.6); q = ease(clamp((t - da) / 0.8))
        if q > 0:
            x, y = x0 + 9 * s, y0 + 19 * s; d = ImageDraw.Draw(img)
            glow(img, [x - 80, y - 80, x + 100, y + 100], (255, 220, 120), 200 * q, 30)
            rect_a(img, (x - 6 * q, y - 6 * q, x + s + 30 * q, y + s + 6 * q), (150, 100, 50), 1, 3, (255, 230, 150), 3)
            text_a(img, (x + s / 2, y - 40 - 20 * q), "9 / 19", F("anton", 44), (255, 230, 150), q, "mm", shadow=6)
        ca = sc.get("count_at", D * 0.88)
        if t >= ca:
            q = clamp((t - ca) / 0.4); rect_a(img, (180, 880, 700, 970), (40, 26, 14), 0.9 * q, 18, T["accent"], 3)
            text_a(img, (440, 925), "7,000 SETS BY 1897", F("anton", 52), WHITE, q, "mm")
    if name == "committee":
        ba = sc.get("bars_at", D * 0.3)
        for i, (lab, v) in enumerate(sc.get("bars", [])):
            q = ease(clamp((t - ba - i * 0.8) / 1.2)); x = 240 + i * 1120 if False else 300; y = 220 + i * 150
            rect_a(img, (x, y, x + 1300, y + 90), (20, 16, 12), 0.85 * clamp((t - ba) / 0.3), 18)
            rect_a(img, (x, y, x + max(20, 1300 * v * q), y + 90), T["accent"] if i else (150, 140, 130), clamp((t - ba) / 0.3), 18)
            text_a(img, (x + 24, y + 45), lab, F("disp", 40, "Black"), (20, 16, 12) if q > 0.5 else WHITE, clamp((t - ba) / 0.3), "lm")
        sa = sc.get("stamp_at", D * 0.75)
        if t >= sa:
            q = back(clamp((t - sa) / 0.4)); f = F("anton", int(110 * clamp(q, 0.2, 1.2)))
            lay = Image.new("RGBA", (900, 220), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
            ld.rounded_rectangle([10, 10, 890, 210], 20, outline=(220, 40, 40, 255), width=12); ld.text((450, 110), "FASTER · CHEAPER · SURER", font=F("anton", 76), fill=(220, 40, 40, 255), anchor="mm")
            lay = lay.rotate(-6, expand=True, resample=Image.BICUBIC); paste_a(img, lay, (500, 560), clamp((t - sa) / 0.15))
    if name == "teagarden":
        for k in range(60):                                                     # light rain
            x = (k * 97 + tg * 300) % W; y = (k * 53 + tg * 900) % H; d.line([x, y, x - 6, y + 26], fill=(180, 200, 230, 90), width=2)
        ca = sc.get("cal_at", D * 0.6); q = back(clamp((t - ca) / 0.6))
        if q > 0:
            w_, h_ = int(520 * clamp(q, 0.05, 1.1)), int(620 * clamp(q, 0.05, 1.1)); x, y = 1200 - w_ / 2 + 100, 520 - h_ / 2
            rect_a(img, (x, y, x + w_, y + h_), (240, 232, 210), 1, 8, (120, 100, 70), 4)
            if q > 0.7:
                text_a(img, (x + w_ / 2, y + 50), "1898", F("anton", 60), (140, 40, 40), 1, "mm")
                for r_ in range(4):
                    for c in range(7): text_a(img, (x + 50 + c * 64, y + 120 + r_ * 70), str(r_ * 7 + c + 1), F("inter", 28, "Bold"), (90, 80, 70), 1, "mm")
                fp = S.fp_img(150, 190, 11, (60, 50, 70), 0.75); img.alpha_composite(fp, (int(x + w_ - 200), int(y + h_ - 230)))
                glow(img, [x + w_ - 240, y + h_ - 260, x + w_ - 20, y + h_ - 20], (255, 80, 60), 90 + 40 * math.sin(tg * 4), 30)
    if name == "court":
        ha = sc.get("hit_at", D * 0.75)
        if t >= ha:
            q = clamp((t - ha) / 0.3)
            for j, x in enumerate((760, 1000)):
                rect_a(img, (x, 300, x + 200, 560), (240, 232, 210), q, 8, (120, 100, 70), 3)
                img.alpha_composite(S.fp_img(160, 200, 11, (60, 50, 70), 0.85 * q), (x + 20, 330))
            rect_a(img, (820, 590, 1140, 670), (30, 130, 70), q, 16); text_a(img, (980, 630), "MATCH", F("anton", 56), WHITE, q, "mm")
        g = clamp((t - ha + 0.4) / 0.4); ang = 60 * (1 - g) if t < ha else 0
        gx, gy = 1640, 600; d = ImageDraw.Draw(img)
        d.line([gx, gy, gx + 140 * math.cos(math.radians(200 + ang)), gy + 140 * math.sin(math.radians(200 + ang))], fill=(70, 40, 20, 255), width=14)
        hx, hy = gx + 140 * math.cos(math.radians(200 + ang)), gy + 140 * math.sin(math.radians(200 + ang))
        d.rounded_rectangle([hx - 40, hy - 26, hx + 40, hy + 26], 8, fill=(90, 50, 24, 255))
    if name == "telegraph":
        code = "AU·OW·IR·1/1·20/14·" * 3
        for k in range(18):
            ph = (tg * 0.25 + k / 18) % 1; x = 1300 - ph * 1300; y = 560 - ph * 440 + 20
            text_a(img, (x, y), code[k % len(code)], F("mono", 34), (255, 230, 140), 0.9 * math.sin(ph * math.pi), "mm", shadow=4)
        if int(tg * 6) % 2: glow(img, [880, 680, 1040, 780], (255, 230, 150), 160, 20)
    if name == "london":
        for k in range(3):
            fog = Image.new("RGBA", (W, H), (0, 0, 0, 0)); x = (tg * (20 + k * 12) + k * 500) % (W + 800) - 800
            ImageDraw.Draw(fog).ellipse([x, 500 + k * 120, x + 1400, 900 + k * 120], fill=(210, 210, 215, 50)); img.alpha_composite(fog.filter(ImageFilter.GaussianBlur(60)))
    if name == "credit":
        ra = sc.get("reveal_at", D * 0.25); q = clamp(t / 0.6)
        rect_a(img, (420, 200, 1500, 420), (40, 30, 18), q, 20, (200, 160, 80), 6)
        text_a(img, (960, 270), "HENRY", F("anton", 90), (230, 200, 130), q, "mm", shadow=6)
        text_a(img, (960, 360), "CLASSIFICATION SYSTEM", F("disp", 46, "Black"), (230, 200, 130), q, "mm")
        q2 = clamp((t - ra) / 0.6)
        if q2 > 0:
            glow(img, [500, 440, 1420, 760], (255, 210, 120), 140 * q2, 60)
            text_a(img, (960, 500), "DEVELOPED BY", F("mono", 34), T["accent"], q2, "mm")
            text_a(img, (960, 600), "AZIZUL HAQUE · HEM CHANDRA BOSE", fit_font("anton", 86, "AZIZUL HAQUE · HEM CHANDRA BOSE", 1500), WHITE, q2, "mm", shadow=10)
        ma = sc.get("medal_at", D * 0.55); q3 = back(clamp((t - ma) / 0.5))
        for j, (lab, x) in enumerate((("KHAN BAHADUR", 700), ("RAI BAHADUR", 1220))):
            if q3 <= 0: break
            r = 60 * clamp(q3, 0, 1.15); d = ImageDraw.Draw(img)
            d.polygon([(x - 30, 680), (x + 30, 680), (x + 20, 750), (x - 20, 750)], fill=(160, 30, 40, 255))
            d.ellipse([x - r, 770 - r, x + r, 770 + r], fill=(220, 180, 80, 255), outline=(150, 110, 40, 255), width=6)
            text_a(img, (x, 862), lab, F("disp", 34, "Black"), WHITE, clamp(q3, 0, 1), "mm")
            text_a(img, (x, 908), "₹5,000", F("anton", 40), T["accent"], clamp(q3, 0, 1), "mm")

# ---------------------------------------------------------------- the toon scene
_bodies = {}
def cast_at(c, t):
    w = c.get("walk")
    if not w: return c.get("x0", 960), None, False
    p = clamp((t - w[0]) / max(0.1, w[1] - w[0]))
    x = c["x0"] + (c["x1"] - c["x0"]) * ease(p) if False else c["x0"] + (c["x1"] - c["x0"]) * p
    walking = 0 < p < 1
    return x, (t * 7.5 if walking else None), walking

def sc_toon(img, sc, t, D, tg, k):
    name = sc.get("set", "street"); base = get_set(name)
    frame = base.copy(); set_fx(frame, name, sc, t, D, tg)
    gy = {"office": 990, "measure": 990, "college": 1000, "drawers": 1000, "committee": 990, "writers": 960, "court": 1000,
          "telegraph": 1000, "london": 990, "street": 990, "finale": 990}.get(name, 990)
    scale = {"drawers": 0.8, "court": 0.85, "telegraph": 0.85, "office": 0.85, "measure": 0.85, "committee": 0.85}.get(name, 0.88)
    for i, c in enumerate(sc.get("cast", [])):
        x, ph, walking = cast_at(c, t)
        if x < -300 or x > W + 300: continue
        face = c.get("face", 1 if c.get("x1", x) >= c.get("x0", x) else -1)
        talk = c.get("talk", True) and not walking and (int(tg * 0.5 + i) % 2 == 0)
        pose = c.get("pose", "down")
        if walking and pose not in ("books", "file"): pose = "down"
        body = person(c["who"], tg, ph, talk, pose, blink_seed=i * 1.3)
        if face < 0: body = body.transpose(Image.FLIP_LEFT_RIGHT)
        if scale != 1: body = body.resize((int(body.width * scale), int(body.height * scale)), Image.LANCZOS)
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse([x - 120 * scale, gy - 18, x + 120 * scale, gy + 18], fill=(0, 0, 0, 110))
        frame.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
        sway = 0 if walking else 2 * math.sin(tg * 1.6 + i)
        frame.alpha_composite(body, (int(x - body.width / 2 + sway), int(gy - body.height)))
    if name == "court":
        dd = ImageDraw.Draw(frame); dd.rectangle([1100, 760, 1760, 990], fill=(96, 60, 36, 255), outline=(60, 38, 24, 255), width=8)
        for k in range(4): dd.rectangle([1130 + k * 160, 790, 1250 + k * 160, 960], outline=(70, 44, 26, 255), width=5)
    # slow camera push-in
    z = 1.0 + 0.045 * (t / max(D, 0.1)); cw, ch = W / z, H / z
    cam = frame.crop((int((W - cw) / 2), int((H - ch) / 2 + (H - ch) * 0.1), int((W + cw) / 2), int((H + ch) / 2 + (H - ch) * 0.1))).resize((W, H), Image.BILINEAR)
    img.paste(cam, (0, 0))
    # cinematic bars + captions
    a = clamp(t / 0.5); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 56], fill=(0, 0, 0, 255)); d.rectangle([0, H - 56, W, H], fill=(0, 0, 0, 255))
    if sc.get("place"):
        s = typed(sc["place"], prog(t, 0.3, 0.9)); f = F("mono", 30); w = d.textlength(s, font=f)
        rect_a(img, (60, 90, 60 + w + 44, 146), (0, 0, 0), 0.6 * a, 12); text_a(img, (82, 118), s, f, T["accent"], a, "lm")
    if sc.get("title"):
        for i, s in enumerate(sc["title"]):
            ta = sc.get("title_at", 1.0) + i * 0.4; q = back(clamp((t - ta) / 0.5))
            text_a(img, (90, 200 + i * 150), s, F("anton", int(140 * clamp(q, 0.3, 1.1))), WHITE if i == 0 else T["accent"], clamp((t - ta) / 0.3), shadow=14)
    if sc.get("line"):
        la = sc.get("line_at", 1.5); q = clamp((t - la) / 0.5); s = sc["line"]; f = fit_font("disp", 46, s, 1500, "Black"); w = d.textlength(s, font=f)
        rect_a(img, (W / 2 - w / 2 - 40, H - 170, W / 2 + w / 2 + 40, H - 96), (0, 0, 0), 0.55 * q, 16)
        text_a(img, (W / 2, H - 133), s, f, WHITE, q, "mm", shadow=6)
    paste_a(img, R.LOGO.resize((64, 64), Image.LANCZOS), (W - 100, 72), 0.9)
    if sc.get("cast") or name in ("river",):
        text_a(img, (W - 30, H - 28), "Illustration · not actual likeness", F("inter", 18), (180, 175, 165), 0.9, "rm")

R.SCENE_FN.update({"toon": sc_toon})

if __name__ == "__main__":
    R.main()
