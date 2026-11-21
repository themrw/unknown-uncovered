#!/usr/bin/env python3
"""Unknown Uncovered v2 renderer: themed, cinematic 1080x1920 reels driven by a JSON spec.

usage: uu_render.py spec.json still t1,t2,...   -> out/still_<scene>_<t>.png
       uu_render.py spec.json full              -> out/video_only.mp4
Durations come from <spec dir>/vo/durs.json (written by uu_voice.py).
"""
import json, math, os, subprocess, sys
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.environ.get("UU_ASSETS", os.path.join(HERE, "assets"))
SPEC_PATH = sys.argv[1]
SPEC = json.load(open(SPEC_PATH))
LONG = SPEC.get("format") == "long"          # 16:9 long-form video (scenes in uu_long.py)
W, H, FPS = (1920, 1080, 30) if LONG else (1080, 1920, 30)
WORK = os.path.dirname(os.path.abspath(SPEC_PATH))
OUT = os.path.join(WORK, "out")

# ---------------------------------------------------------------- themes
THEMES = {
    "nuclear": dict(bg=(5, 8, 6), glow=(60, 70, 10), accent=(255, 205, 40), accent2=(150, 255, 90), alert=(255, 70, 60),
                    land=(26, 34, 24), land_edge=(70, 95, 55), ocean=(8, 16, 12), part=(190, 255, 120), motif="radiation"),
    "war": dict(bg=(6, 10, 12), glow=(70, 14, 16), accent=(240, 170, 50), accent2=(110, 210, 150), alert=(232, 64, 70),
                land=(24, 30, 32), land_edge=(70, 90, 90), ocean=(8, 14, 18), part=(255, 140, 80), motif="radar"),
    "money": dict(bg=(8, 7, 4), glow=(70, 50, 8), accent=(255, 200, 60), accent2=(90, 220, 140), alert=(255, 90, 70),
                  land=(34, 30, 20), land_edge=(110, 95, 55), ocean=(12, 11, 8), part=(255, 215, 120), motif="chart"),
    "space": dict(bg=(4, 4, 12), glow=(30, 20, 80), accent=(140, 200, 255), accent2=(255, 140, 220), alert=(255, 90, 120),
                  land=(22, 26, 48), land_edge=(80, 100, 170), ocean=(6, 8, 22), part=(220, 230, 255), motif="stars"),
    "missile": dict(bg=(4, 7, 16), glow=(18, 36, 86), accent=(255, 152, 40), accent2=(110, 205, 255), alert=(255, 58, 72),
                    land=(20, 30, 48), land_edge=(70, 112, 165), ocean=(6, 12, 26), part=(150, 210, 255), motif="radar"),
    "gold": dict(bg=(13, 9, 3), glow=(92, 62, 12), accent=(255, 198, 64), accent2=(255, 228, 160), alert=(255, 92, 58),
                 land=(42, 31, 12), land_edge=(160, 118, 42), ocean=(15, 11, 4), part=(255, 214, 120), motif="ingot"),
    "desert": dict(bg=(9, 8, 16), glow=(70, 42, 18), accent=(255, 178, 70), accent2=(240, 222, 190), alert=(255, 66, 56),
                   land=(46, 34, 24), land_edge=(170, 125, 70), ocean=(10, 12, 24), part=(255, 205, 140), motif="satellite"),
    "corporate": dict(bg=(6, 8, 12), glow=(22, 40, 70), accent=(120, 196, 255), accent2=(210, 222, 236), alert=(255, 76, 76),
                      land=(22, 28, 38), land_edge=(80, 100, 130), ocean=(8, 11, 18), part=(170, 200, 235), motif="badge"),
    "history": dict(bg=(14, 10, 6), glow=(70, 45, 15), accent=(235, 190, 110), accent2=(200, 150, 90), alert=(200, 70, 50),
                    land=(48, 38, 26), land_edge=(120, 95, 60), ocean=(20, 15, 10), part=(240, 210, 160), motif="parchment"),
    "forensic": dict(bg=(5, 10, 14), glow=(12, 58, 66), accent=(90, 228, 220), accent2=(255, 196, 96), alert=(240, 62, 72),
                     land=(20, 36, 42), land_edge=(60, 130, 135), ocean=(6, 12, 16), part=(160, 240, 235), motif="fingerprint"),
    "pharma": dict(bg=(246, 248, 245), glow=(0, 0, 0), accent=(0, 140, 130), accent2=(240, 120, 20), alert=(214, 48, 60),
                   land=(206, 224, 216), land_edge=(120, 160, 150), ocean=(228, 238, 244), part=(205, 228, 220), motif="pill", light=True),
    "peace": dict(bg=(4, 9, 16), glow=(18, 56, 100), accent=(100, 185, 255), accent2=(255, 214, 120), alert=(255, 120, 60),
                  land=(22, 34, 48), land_edge=(80, 130, 180), ocean=(6, 14, 26), part=(150, 210, 255), motif="laurel"),
    "news": dict(bg=(243, 244, 247), glow=(0, 0, 0), accent=(16, 40, 92), accent2=(196, 28, 44), alert=(200, 30, 45), green=(14, 132, 78), amber=(206, 132, 0),
                 land=(206, 213, 228), land_edge=(120, 135, 170), ocean=(229, 234, 243), part=(200, 210, 230), motif="none", light=True,
                 blobs=((0.15, 0.18, 520, (226, 232, 244)), (0.9, 0.35, 560, (236, 238, 246)), (0.3, 0.85, 600, (230, 236, 246)), (0.85, 0.9, 420, (238, 240, 246)))),
    "oil": dict(bg=(7, 6, 6), glow=(88, 34, 8), accent=(255, 150, 40), accent2=(120, 200, 215), alert=(240, 60, 50),
                land=(34, 26, 20), land_edge=(130, 90, 55), ocean=(10, 9, 10), part=(255, 170, 90), motif="refinery"),
}
T = THEMES[SPEC.get("theme", "war")]
WHITE = (242, 242, 238); MUTED = (150, 156, 150); BLACK = (0, 0, 0)
LIGHT = bool(T.get("light"))
PUNCH = bool(SPEC.get("punch"))   # Shorts v2: instant first frame, clean chrome, burned-in Hindi captions
if LIGHT: WHITE = (22, 30, 40); MUTED = (92, 102, 112)     # "WHITE" is the main text ink; on light themes it is dark

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_io(x): x = clamp(x); return x * x * (3 - 2 * x)
def back(x):
    x = clamp(x); c = 1.6; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def prog(t, s, d): return ease((t - s) / d)

_fc = {}
def F(name, size, wght=None):
    k = (name, size, wght)
    if k not in _fc:
        paths = {"inter": "/usr/share/fonts/opentype/inter/Inter-{w}.otf", "disp": "/usr/share/fonts/opentype/inter/InterDisplay-{w}.otf",
                 "mono": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", "anton": os.path.join(ASSETS, "Anton-Regular.ttf"),
                 "hindi": os.path.join(ASSETS, "Mukta-ExtraBold.ttf"), "unb": os.path.join(ASSETS, "Unbounded.ttf")}
        p = paths[name].format(w=wght or "Bold")
        f = ImageFont.truetype(p, size, layout_engine=ImageFont.Layout.RAQM if name == "hindi" else ImageFont.Layout.BASIC)
        if name == "unb": f.set_variation_by_axes([wght or 800])
        _fc[k] = f
    return _fc[k]

# ---------------------------------------------------------------- drawing helpers
def fit_font(kind, size, s, max_w, weight=None):
    """Largest font <= size whose rendering of s fits max_w pixels."""
    while size > 24:
        f = F(kind, size, weight) if weight else F(kind, size)
        if ImageDraw.Draw(Image.new("L", (1, 1))).textlength(s, font=f) <= max_w: return f
        size -= 4
    return F(kind, size, weight) if weight else F(kind, size)

def text_a(img, xy, s, f, fill, alpha=1.0, anchor="la", stroke=0, shadow=0):
    if alpha <= 0 or not s: return
    d = ImageDraw.Draw(img)
    l, t, r, b = d.textbbox(xy, s, font=f, anchor=anchor, stroke_width=stroke)
    pad = 6 + shadow
    l, t, r, b = int(l) - pad, int(t) - pad, int(r) + pad, int(b) + pad + shadow
    lay = Image.new("RGBA", (max(1, r - l), max(1, b - t)), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    A = int(255 * clamp(alpha))
    if shadow:
        sc_ = (255, 255, 255, int(A * 0.85)) if LIGHT and sum(fill[:3]) < 400 else (0, 0, 0, int(A * 0.75))
        ld.text((xy[0] - l, xy[1] - t + shadow), s, font=f, fill=sc_, anchor=anchor, stroke_width=stroke, stroke_fill=sc_)
    ld.text((xy[0] - l, xy[1] - t), s, font=f, fill=fill + (A,), anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0, A))
    cl, ct = -min(l, 0), -min(t, 0)
    if cl or ct: lay = lay.crop((cl, ct, lay.width, lay.height))
    img.alpha_composite(lay, (max(l, 0), max(t, 0)))

def rect_a(img, box, fill, alpha=1.0, r=0, outline=None, width=0):
    if alpha <= 0: return
    x0, y0, x1, y1 = [int(v) for v in box]
    if x1 <= x0 or y1 <= y0: return
    lay = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
    ImageDraw.Draw(lay).rounded_rectangle((0, 0, x1 - x0 - 1, y1 - y0 - 1), radius=r,
        fill=(fill + (int(255 * clamp(alpha)),)) if fill else None,
        outline=(outline + (int(255 * clamp(alpha)),)) if outline else None, width=width)
    img.alpha_composite(lay, (x0, y0))

def alpha_mul(im, a):
    if a >= 1: return im
    im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a))); return im

def paste_a(img, src, xy, alpha=1.0):
    if alpha > 0: img.alpha_composite(alpha_mul(src, alpha), (int(xy[0]), int(xy[1])))

def typed(s, p): return s[: int(round(len(s) * clamp(p)))]

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

def silhouette(src, col=(20, 22, 20)):
    a = src.getchannel("A"); s = Image.new("RGBA", src.size, col + (255,)); s.putalpha(a); return s

LOGO = Image.open(os.path.join(ASSETS, "logo_uu.png")).convert("RGBA").resize((92, 92), Image.LANCZOS)

# ---------------------------------------------------------------- globe
GEO = json.load(open(os.path.join(ASSETS, "countries.geojson")))
COUNTRIES = []   # (iso2, [rings as (lon, lat) radians arrays])
CENTROID = {}
for ft in GEO["features"]:
    p = ft["properties"]; iso = p.get("ISO_A2_EH") or p.get("ISO_A2")
    g = ft["geometry"]; polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    rings = [np.radians(np.array(poly[0], dtype=np.float64)) for poly in polys]
    COUNTRIES.append((iso, rings))
    if p.get("LABEL_X") is not None: CENTROID[iso] = (p["LABEL_Y"], p["LABEL_X"])

class Globe:
    def __init__(self, R):
        self.R = R; S = 2 * R + 160; self.S = S; c = S / 2
        y, x = np.mgrid[0:S, 0:S].astype(np.float32) - c
        rr = np.hypot(x, y) / R
        ocean = np.zeros((S, S, 4), np.float32)
        base = np.array(T["ocean"], np.float32); hi = np.array(T["land_edge"], np.float32) * 0.35
        shade = np.clip(1 - rr, 0, 1) ** 0.5
        ocean[..., :3] = base + hi * shade[..., None] * 0.6
        ocean[..., 3] = (rr <= 1) * 255
        self.ocean = Image.fromarray(np.clip(ocean, 0, 255).astype(np.uint8), "RGBA")
        atm = np.clip(1 - np.abs(rr - 1.0) / 0.09, 0, 1) ** 2 * (rr > 0.96)
        a = np.zeros((S, S, 4), np.uint8); a[..., :3] = T["accent2"]; a[..., 3] = (atm * 120).astype(np.uint8)
        self.atmo = Image.fromarray(a, "RGBA").filter(ImageFilter.GaussianBlur(6))
        lit = np.clip(((-x - y * 0.6) / (R * 1.4) + 0.5), 0, 1) * (rr <= 1)
        l = np.zeros((S, S, 4), np.uint8); l[..., :3] = 255; l[..., 3] = (lit ** 2 * 38).astype(np.uint8)
        self.light = Image.fromarray(l, "RGBA")

    def project(self, lon, lat, lat0, lon0):
        cl = np.cos(lat); x = cl * np.sin(lon - lon0)
        y = np.cos(lat0) * np.sin(lat) - np.sin(lat0) * cl * np.cos(lon - lon0)
        vis = np.sin(lat0) * np.sin(lat) + np.cos(lat0) * cl * np.cos(lon - lon0)
        n = np.hypot(x, y) + 1e-9
        x = np.where(vis < 0, x / n, x); y = np.where(vis < 0, y / n, y)
        c = self.S / 2
        return np.stack([c + x * self.R, c - y * self.R], 1), vis

    def render(self, lat0d, lon0d, highlight=None, hl_alpha=1.0, dim_others=0.0, pulse=0.0, hide=False):
        lat0, lon0 = math.radians(lat0d), math.radians(lon0d)
        im = self.ocean.copy(); d = ImageDraw.Draw(im)
        gcol = T["land_edge"] + (40,)
        for la in range(-60, 90, 30):
            lon = np.radians(np.linspace(-180, 180, 120)); lat = np.full_like(lon, math.radians(la))
            pts, vis = self.project(lon, lat, lat0, lon0)
            seg = [tuple(p) for p, v in zip(pts, vis) if v > 0]
            if len(seg) > 1: d.line(seg, fill=gcol, width=1)
        for lo in range(-180, 180, 30):
            lat = np.radians(np.linspace(-90, 90, 90)); lon = np.full_like(lat, math.radians(lo))
            pts, vis = self.project(lon, lat, lat0, lon0)
            seg = [tuple(p) for p, v in zip(pts, vis) if v > 0]
            if len(seg) > 1: d.line(seg, fill=gcol, width=1)
        hl_mask = Image.new("L", im.size, 0); hd = ImageDraw.Draw(hl_mask)
        land = tuple(int(c * (1 - 0.45 * dim_others)) for c in T["land"])
        edge = tuple(int(c * (1 - 0.45 * dim_others)) for c in T["land_edge"])
        for iso, rings in COUNTRIES:
            for r in rings:
                pts, vis = self.project(r[:, 0], r[:, 1], lat0, lon0)
                if (vis > 0).sum() < 2: continue
                poly = [tuple(p) for p in pts]
                if highlight and iso in highlight:
                    hd.polygon(poly, fill=255)
                else:
                    d.polygon(poly, fill=land + (255,), outline=edge + (255,))
        if highlight and hl_alpha > 0:
            col = T["alert"] if hide else T["accent"]
            glow = Image.new("RGBA", im.size, col + (0,)); glow.putalpha(hl_mask.filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.9 * hl_alpha)))
            fill = Image.new("RGBA", im.size, col + (0,)); fill.putalpha(hl_mask.point(lambda v: int(v * (0.85 + 0.15 * pulse) * hl_alpha)))
            base_land = Image.new("RGBA", im.size, land + (0,)); base_land.putalpha(hl_mask)
            im.alpha_composite(base_land); im.alpha_composite(glow); im.alpha_composite(fill)
        im.alpha_composite(self.light)
        ring = Image.new("L", im.size, 0); ImageDraw.Draw(ring).ellipse([self.S / 2 - self.R] * 2 + [self.S / 2 + self.R] * 2, fill=255)
        im.putalpha(ImageChops.multiply(im.getchannel("A"), ring))
        im.alpha_composite(self.atmo)
        return im

    def point(self, latd, lond, lat0d, lon0d):
        pts, vis = self.project(np.array([math.radians(lond)]), np.array([math.radians(latd)]), math.radians(lat0d), math.radians(lon0d))
        return pts[0], vis[0]

GLOBE = Globe(int(SPEC.get("globe_radius", 330)))

# ---------------------------------------------------------------- background, particles, grain, motif
BW, BH = W + 120, H + 120
def make_bg():
    y, x = np.mgrid[0:BH, 0:BW].astype(np.float32)
    f = (np.sin(x / 230) + np.sin(y / 280 + 1.3) + np.sin((x + y) / 350) + 0.6 * np.sin((x - 1.7 * y) / 160 + 2))
    band = np.abs((f * 3.0) % 1 - 0.5) < 0.03
    img = np.zeros((BH, BW, 3), np.float32) + np.array(T["bg"], np.float32)
    img[band] += np.array(T["land_edge"], np.float32) * 0.18
    img[(y.astype(int) % 4) == 0] *= 0.88
    glow = np.exp(-(((x - BW / 2) / 650) ** 2 + ((y - BH * 0.38) / 620) ** 2))[..., None]
    img += glow * np.array(T["glow"], np.float32)
    vig = 1 - 0.65 * np.clip(((x - BW / 2) / (BW * 0.72)) ** 2 + ((y - BH / 2) / (BH * 0.66)) ** 2, 0, 1)
    img *= vig[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
def make_bg_light():
    y, x = np.mgrid[0:BH, 0:BW].astype(np.float32)
    img = np.zeros((BH, BW, 3), np.float32) + np.array(T["bg"], np.float32)
    for (cx, cy, r, col) in T.get("blobs", ((0.15, 0.18, 520, (196, 234, 222)), (0.9, 0.35, 560, (210, 226, 248)), (0.3, 0.85, 600, (255, 228, 200)), (0.85, 0.9, 420, (214, 240, 230)))):
        g = np.exp(-(((x - BW * cx) / r) ** 2 + ((y - BH * cy) / r) ** 2))[..., None]
        img = img * (1 - 0.75 * g) + np.array(col, np.float32) * 0.75 * g
    f = (np.sin(x / 230) + np.sin(y / 280 + 1.3) + np.sin((x + y) / 350) + 0.6 * np.sin((x - 1.7 * y) / 160 + 2))
    band = np.abs((f * 3.0) % 1 - 0.5) < 0.022
    img[band] = img[band] * 0.94
    dots = ((x.astype(int) % 48) < 3) & ((y.astype(int) % 48) < 3)
    img[dots] = img[dots] * 0.93
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
BG = make_bg_light() if LIGHT else make_bg()

rng = np.random.default_rng(11)
PART = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(12, 50), rng.uniform(1.2, 3.6), rng.uniform(.25, .9), rng.uniform(0, 6.28)) for _ in range(90)]
GRAIN = [Image.fromarray((rng.normal(128, 22, (H // 2, W // 2))).clip(0, 255).astype(np.uint8)).resize((W, H)) for _ in range(6)]

_motif = {}
def motif_img(R):
    if R in _motif: return _motif[R]
    S = 2 * R + 4; c = S / 2; im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    col = T["accent"] + (255,)
    if T["motif"] == "radiation":
        d.ellipse([c - R, c - R, c + R, c + R], outline=col, width=max(3, R // 14))
        for k in range(3):
            a0 = -90 + k * 120 - 30
            d.pieslice([c - R * 0.82, c - R * 0.82, c + R * 0.82, c + R * 0.82], a0, a0 + 60, fill=col)
        d.ellipse([c - R * 0.24, c - R * 0.24, c + R * 0.24, c + R * 0.24], fill=(0, 0, 0, 0))
        hole = Image.new("L", (S, S), 255); ImageDraw.Draw(hole).ellipse([c - R * 0.24, c - R * 0.24, c + R * 0.24, c + R * 0.24], fill=0)
        im.putalpha(ImageChops.multiply(im.getchannel("A"), hole))
        d = ImageDraw.Draw(im); d.ellipse([c - R * 0.15, c - R * 0.15, c + R * 0.15, c + R * 0.15], fill=col)
    elif T["motif"] == "radar":
        for k in range(1, 5):
            r = R * k / 4; d.ellipse([c - r, c - r, c + r, c + r], outline=col, width=3)
        d.line([c - R, c, c + R, c], fill=col, width=2); d.line([c, c - R, c, c + R], fill=col, width=2)
    elif T["motif"] == "ingot":   # stacked gold bars, outline
        w, h = R * 0.9, R * 0.34
        for (cx, cy) in ((c - w * 0.52, c + h * 0.6), (c + w * 0.52, c + h * 0.6), (c, c - h * 0.55)):
            d.polygon([(cx - w * 0.5, cy + h * 0.5), (cx + w * 0.5, cy + h * 0.5), (cx + w * 0.36, cy - h * 0.5), (cx - w * 0.36, cy - h * 0.5)],
                      outline=col, width=max(3, R // 18))
            d.line([(cx - w * 0.36, cy - h * 0.5), (cx - w * 0.28, cy - h * 0.2), (cx + w * 0.28, cy - h * 0.2), (cx + w * 0.36, cy - h * 0.5)], fill=col, width=2)
    elif T["motif"] == "satellite":   # spy satellite: body + two solar wings + dish
        lw = max(3, R // 20)
        d.rectangle([c - R * 0.22, c - R * 0.3, c + R * 0.22, c + R * 0.3], outline=col, width=lw)
        for sx in (-1, 1):
            x0, x1 = c + sx * R * 0.3, c + sx * R * 1.0
            d.rectangle([min(x0, x1), c - R * 0.2, max(x0, x1), c + R * 0.2], outline=col, width=lw)
            for j in range(1, 4): xx = x0 + (x1 - x0) * j / 4; d.line([xx, c - R * 0.2, xx, c + R * 0.2], fill=col, width=max(2, lw // 2))
            d.line([c + sx * R * 0.22, c, x0, c], fill=col, width=lw)
        d.arc([c - R * 0.2, c + R * 0.28, c + R * 0.2, c + R * 0.62], 180, 360, fill=col, width=lw)
    elif T["motif"] == "badge":   # employee ID card on a lanyard, outline
        w, h, lw = R * 1.1, R * 1.5, max(3, R // 18)
        d.rounded_rectangle([c - w / 2, c - h / 2 + R * 0.2, c + w / 2, c + h / 2 + R * 0.2], radius=int(R * 0.12), outline=col, width=lw)
        d.line([c - R * 0.25, c - h / 2 + R * 0.2, c, c - R * 1.0, c + R * 0.25, c - h / 2 + R * 0.2], fill=col, width=lw)
        d.ellipse([c - R * 0.24, c - R * 0.45, c + R * 0.24, c + R * 0.03], outline=col, width=lw)
        d.arc([c - R * 0.38, c - R * 0.02, c + R * 0.38, c + R * 0.62], 200, 340, fill=col, width=lw)
        for k in range(2): d.line([c - w * 0.32, c + R * (0.62 + k * 0.16), c + w * 0.32, c + R * (0.62 + k * 0.16)], fill=col, width=lw)
    elif T["motif"] == "fingerprint":   # concentric loops, open at the bottom
        lw = max(2, R // 22)
        for k in range(1, 8):
            r = R * k / 7.5; d.arc([c - r * 0.8, c - r, c + r * 0.8, c + r], 200 - k * 4, 340 + k * 4, fill=col, width=lw)
            if k > 2: d.arc([c - r * 0.8, c - r * 0.6, c + r * 0.8, c + r * 1.2], 10, 60, fill=col, width=lw)
    elif T["motif"] == "refinery":   # distillation columns, tank and a flare stack, outline
        lw = max(3, R // 20); base = c + R * 0.8
        d.line([c - R, base, c + R, base], fill=col, width=lw)
        for (x, w, h) in ((-0.55, 0.22, 1.5), (-0.18, 0.16, 1.15), (0.12, 0.2, 1.35)):
            x0 = c + x * R; d.rounded_rectangle([x0, base - h * R, x0 + w * R, base], radius=int(w * R / 2), outline=col, width=lw)
            for j in range(1, 4): d.line([x0, base - h * R * j / 4, x0 + w * R, base - h * R * j / 4], fill=col, width=max(2, lw // 2))
        d.ellipse([c + R * 0.42, base - R * 0.5, c + R * 0.95, base], outline=col, width=lw)
        d.line([c + R * 0.88, base, c + R * 0.88, c - R * 0.9], fill=col, width=lw)
        d.polygon([(c + R * 0.88, c - R * 1.15), (c + R * 0.8, c - R * 0.92), (c + R * 0.96, c - R * 0.92)], fill=T["alert"] + (255,))
    elif T["motif"] == "pill":
        lw = max(3, R // 22)
        for ang in (-30, 30):
            lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
            ld.rounded_rectangle([c - R * 0.75, c - R * 0.26, c + R * 0.75, c + R * 0.26], radius=int(R * 0.26), outline=col, width=lw)
            ld.line([c, c - R * 0.26, c, c + R * 0.26], fill=col, width=lw)
            im.alpha_composite(lay.rotate(ang, center=(c, c), resample=Image.BICUBIC))
    elif T["motif"] == "laurel":   # two olive branches around a globe, outline (peacekeeping)
        lw = max(3, R // 22); r0 = R * 0.52
        d.ellipse([c - r0, c - r0, c + r0, c + r0], outline=col, width=lw)
        d.line([c - r0, c, c + r0, c], fill=col, width=max(2, lw // 2))
        d.ellipse([c - r0 * 0.45, c - r0, c + r0 * 0.45, c + r0], outline=col, width=max(2, lw // 2))
        for sgn in (-1, 1):
            pts = [(c + sgn * R * 0.86 * math.sin(math.radians(a)), c + R * 0.86 * math.cos(math.radians(a))) for a in range(20, 160, 6)]
            d.line(pts, fill=col, width=lw)
            for j, (x, y) in enumerate(pts[1::3]):
                a = math.radians(20 + (j * 3 + 1) * 6); ox, oy = sgn * math.cos(a), -math.sin(a)
                lx, ly = x + ox * R * 0.13 + sgn * R * 0.04, y + oy * R * 0.13
                d.ellipse([lx - R * 0.07, ly - R * 0.035, lx + R * 0.07, ly + R * 0.035], outline=col, width=max(2, lw // 2))
    else:
        d.ellipse([c - R, c - R, c + R, c + R], outline=col, width=4)
    _motif[R] = im; return im

def particles(img, tg):
    d = ImageDraw.Draw(img)
    for (x, y0, sp, s, a, ph) in PART:
        y = (y0 - sp * tg) % H; xx = x + 14 * math.sin(tg * 0.5 + ph)
        fl = 0.55 + 0.45 * math.sin(tg * 3 + ph * 3)
        aa = a * fl
        c = tuple(int(T["bg"][i] + (T["part"][i] - T["bg"][i]) * aa) for i in range(3))
        d.ellipse([xx - s, y - s, xx + s, y + s], fill=c + (255,))

# ---------------------------------------------------------------- chrome (ticker, header, logo, frame)
TICK = SPEC.get("ticker", "")
def make_ticker():
    f = F("mono", 24); w = int(ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(TICK, font=f)) or 1
    im = Image.new("RGBA", (w * 2, 44), tuple(int(c * 0.35) for c in T["alert"]) + (225,)); d = ImageDraw.Draw(im)
    d.text((0, 22), TICK, font=f, fill=(255, 230, 220), anchor="lm"); d.text((w, 22), TICK, font=f, fill=(255, 230, 220), anchor="lm")
    return im, w
TICK_IM, TICK_W = make_ticker()

def brackets(img, box, col, alpha=1.0, L=40, w=4):
    if alpha <= 0: return
    x0, y0, x1, y1 = [int(v) for v in box]
    lay = Image.new("RGBA", (x1 - x0 + 1, y1 - y0 + 1), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    c = col + (int(255 * alpha),); X, Y = x1 - x0, y1 - y0
    for (ax, ay, sx, sy) in [(0, 0, 1, 1), (X, 0, -1, 1), (0, Y, 1, -1), (X, Y, -1, -1)]:
        d.line([ax, ay, ax + sx * L, ay], fill=c, width=w); d.line([ax, ay, ax, ay + sy * L], fill=c, width=w)
    img.alpha_composite(lay, (x0, y0))

def chrome(img, tg, a=1.0, header=True):
    if a <= 0: return
    off = int(tg * 100) % TICK_W
    if LONG:
        paste_a(img, TICK_IM.crop((off, 0, off + W, 44)), (0, H - 44), a * 0.9)
        if header:
            rect_a(img, (56, 40, 64, 72), T["alert"], a)
            text_a(img, (78, 56), SPEC.get("header", ""), F("inter", 24, "Bold"), WHITE, a, "lm")
            text_a(img, (56, 92), SPEC.get("source", ""), F("inter", 18, "Regular"), MUTED, a, "lm")
        paste_a(img, LOGO.resize((72, 72), Image.LANCZOS), (W - 56 - 72, 30), a * 0.92)
        brackets(img, (24, 20, W - 24, H - 58), T["accent2"], 0.22 * a, 40, 3)
        return
    if PUNCH:   # clean Shorts look: no ticker, no header/source lines
        paste_a(img, LOGO.resize((80, 80), Image.LANCZOS), (W - 60 - 80, 150), a * 0.92)
        return
    paste_a(img, TICK_IM.crop((off, 0, off + W, 44)), (0, 118), a)
    if header:
        rect_a(img, (70, 190, 80, 228), T["alert"], a)
        text_a(img, (96, 209), SPEC.get("header", ""), F("inter", 30, "Bold"), WHITE, a, "lm")
        text_a(img, (70, 252), SPEC.get("source", ""), F("inter", 24, "Regular"), MUTED, a, "lm")
    paste_a(img, LOGO, (W - 70 - 92, 176), a * 0.92)
    brackets(img, (36, 96, W - 36, 1650), T["accent2"], 0.25 * a, 46, 3)

# ---------------------------------------------------------------- camera (globe target per scene)
def scene_view(sc):
    if sc.get("code") and sc["code"] in CENTROID:
        la, lo = CENTROID[sc["code"]]; return (max(-45, min(45, la)), lo)
    v = sc.get("view")
    return tuple(v) if v else (20.0, 60.0)

# ---------------------------------------------------------------- scenes
def big_number(img, s, x, y, size, col, a, anchor="la"):
    text_a(img, (x, y), s, F("anton", size), col, a, anchor, shadow=8)

def sc_hook(img, sc, t, D, tg, k):
    """Cold open: dark rotating globe, flicker, redacted file, no answers revealed."""
    lon = 40 + tg * 6
    g = GLOBE.render(18, lon, highlight=None, dim_others=0.6)
    ga = 0.25 + 0.45 * prog(t, 0.2, 2.5)
    paste_a(img, g.resize((int(g.width * 1.25),) * 2, Image.BILINEAR), (W / 2 - g.width * 1.25 / 2, 980 - g.width * 1.25 / 2), ga)
    for i, (la, lo) in enumerate(sc.get("blips", [])):
        (px, py), vis = GLOBE.point(la, lo, 18, lon)
        if vis > 0.15:
            ph = (tg * 1.3 + i * 0.37) % 1
            cx = W / 2 - g.width * 1.25 / 2 + px * 1.25; cy = 980 - g.width * 1.25 / 2 + py * 1.25
            rr = 10 + ph * 46; aa = (1 - ph) * prog(t, 1.0 + i * 0.3, 0.4)
            ImageDraw.Draw(img).ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=T["alert"] + (int(220 * aa),), width=3)
            ImageDraw.Draw(img).ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=T["alert"] + (int(255 * prog(t, 1.0 + i * 0.3, 0.3)),))
    lines = sc.get("file", [])
    for i, s in enumerate(lines):
        st = 0.3 + i * 0.5
        text_a(img, (80, 300 + i * 46), typed(s, prog(t, st, 0.6)), F("mono", 30), T["accent2"], 1)
    rect_a(img, (80, 300 + len(lines) * 46 + 8, 80 + int(560 * prog(t, 1.4, 0.8)), 300 + len(lines) * 46 + 42), (0, 0, 0), 0.95)
    for i, (s, col) in enumerate(sc["title"]):
        st = sc.get("title_at", 1.8) + i * 0.45; p = back((t - st) / 0.55)
        fl = 1.0 if t - st > 0.5 else (0.4 + 0.6 * (int((t - st) * 30) % 2))
        text_a(img, (80 - (1 - p) * 60, 470 + i * 150), s, F("disp", 132, "Black"), T[col] if col in T else WHITE, clamp((t - st) / 0.25) * fl, shadow=10)

def sc_tease(img, sc, t, D, tg, k):
    lon = 60 + tg * 5
    g = GLOBE.render(15, lon, dim_others=0.5)
    paste_a(img, g, (W / 2 - g.width / 2, 1060 - g.width / 2), 0.5)
    chrome(img, tg, prog(t, 0, 0.5))
    text_a(img, (80, 330), typed(sc.get("kicker", ""), prog(t, 0.1, 0.8)), F("mono", 32), T["accent2"], 1)
    big_number(img, sc["big"], 80, 380, 300, T["accent"], prog(t, 0.2, 0.4))
    text_a(img, (90, 720), sc["big_label"], F("disp", 52 if len(sc["big_label"]) > 18 else 64, "Black"), WHITE, prog(t, 0.5, 0.4), shadow=6)
    n = sc.get("cards", 5); cw = 170; gap = (W - 160 - n * cw) / max(1, n - 1)
    for i in range(n):
        st = 0.9 + i * 0.18; a = clamp((t - st) / 0.3); dy = (1 - back((t - st) / 0.5)) * 80; x = 80 + i * (cw + gap)
        rect_a(img, (x, 1500 + dy, x + cw, 1640 + dy), (16, 18, 16), a * 0.92, 18, T["alert"] if i == n - 1 else T["land_edge"], 3)
        text_a(img, (x + cw / 2, 1570 + dy), "?", F("anton", 96), T["alert"] if i == n - 1 else MUTED, a, "mm")
    text_a(img, (80, 1380), typed(sc.get("hook", ""), prog(t, 1.8, 1.2)), F("disp", 52, "Bold"), T["accent"], 1, shadow=5)

def sc_stat(img, sc, t, D, tg, k):
    lat, lon = scene_view(sc); lon += (t if sc.get("highlight") else tg) * 3
    g = GLOBE.render(lat, lon, highlight=sc.get("highlight"), hl_alpha=prog(t, 0.6, 0.8) if sc.get("highlight") else 1,
                     dim_others=0.35 if sc.get("highlight") else 0.2, pulse=0.5 + 0.5 * math.sin(tg * 5) if sc.get("highlight") else 0)
    paste_a(img, g, (W / 2 - g.width / 2, 1170 - g.width / 2), 0.85 * prog(t, 0, 0.6))
    m = motif_img(170); paste_a(img, m.rotate(-tg * 12, resample=Image.BILINEAR), (W - 300, 330), 0.10)
    chrome(img, tg)
    text_a(img, (80, 330), typed(sc["kicker"], prog(t, 0.1, 0.9)), F("mono", 30), T["accent2"], 1)
    v = sc["value"] * prog(t, 0.3, max(1.2, D * 0.45))
    big_number(img, sc.get("fmt", "{:,.0f}").format(v), 80, 380, 250, WHITE, prog(t, 0.2, 0.3))
    text_a(img, (88, 680), sc["label"], fit_font("disp", 84, sc["label"], W - 170, "Black"), T["accent"], prog(t, 0.5, 0.4), shadow=6)
    for i, (kk, s) in enumerate(sc.get("items", [])):
        st = D * 0.35 + i * D * 0.18; a = clamp((t - st) / 0.3); dx = (1 - back((t - st) / 0.5)) * -120; y = 830 + i * 150
        rect_a(img, (80 + dx, y, 1000 + dx, y + 124), (10, 14, 12), a * 0.85, 14, T["land_edge"], 2)
        rect_a(img, (80 + dx, y, 92 + dx, y + 124), T["accent"], a)
        text_a(img, (122 + dx, y + 12), kk, F("anton", 62), WHITE, a)
        text_a(img, (122 + dx, y + 80), s, F("inter", 32, "Medium"), MUTED, a)


def draw_reach(img, gx, gy, lat0d, lon0d, origin, km, p, col):
    """Expanding range ring around `origin`: how far the missile can reach (no target implied)."""
    if p <= 0: return
    c = GLOBE.S / 2
    la1, lo1 = math.radians(origin[0]), math.radians(origin[1])
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for frac, w, al in ((1.0, 6, 255), (0.82, 3, 110), (0.6, 2, 60)):
        dl = min(math.pi * 0.995, p * frac * km / 6371.0)
        b = np.linspace(0, 2 * np.pi, 240)
        la = np.arcsin(np.sin(la1) * np.cos(dl) + np.cos(la1) * np.sin(dl) * np.cos(b))
        lo = lo1 + np.arctan2(np.sin(b) * np.sin(dl) * np.cos(la1), np.cos(dl) - np.sin(la1) * np.sin(la))
        pts, vis = GLOBE.project(lo, la, math.radians(lat0d), math.radians(lon0d))
        for i in range(1, len(b)):
            if vis[i] > 0 and vis[i - 1] > 0:
                d.line([(gx + pts[i - 1][0], gy + pts[i - 1][1]), (gx + pts[i][0], gy + pts[i][1])], fill=col + (al,), width=w)
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(7))); img.alpha_composite(lay)

def sc_rank(img, sc, t, D, tg, k):
    """Countdown card: globe swings to the country (still hidden), suspense beat, then flag + name reveal."""
    lat, lon = scene_view(sc)
    prev = SCENES[k - 1][0] if k > 0 else sc
    plat, plon = scene_view(prev)
    dl = ((lon - plon + 180) % 360) - 180
    m = ease_io(t / 1.2)
    clat, clon = plat + (lat - plat) * m, plon + dl * m + t * 1.5
    reveal = sc.get("reveal_at", 1.4)
    hide = t < reveal
    pulse = 0.5 + 0.5 * math.sin(tg * 6)
    # while hidden, no country fill (its shape would give the answer away): only the pulsing target rings below
    g = GLOBE.render(clat, clon, highlight=None if hide else [sc["code"]] + sc.get("also", []),
                     hl_alpha=prog(t, reveal, 0.4), dim_others=0.35, pulse=pulse, hide=hide)
    gx, gy = W / 2 - g.width / 2, 700 - g.width / 2
    paste_a(img, g, (gx, gy), 1)
    (px, py), vis = GLOBE.point(*CENTROID.get(sc["code"], (lat, lon)), clat, clon)
    if vis > 0 and t > 0.8:
        cx, cy = gx + px, gy + py
        for j in range(2):
            ph = (tg * 0.9 + j * 0.5) % 1; rr = 14 + ph * 70
            ImageDraw.Draw(img).ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=(T["alert"] if hide else T["accent"]) + (int(200 * (1 - ph)),), width=3)
    if sc.get("reach_km") and not hide:
        draw_reach(img, gx, gy, clat, clon, CENTROID.get(sc["code"], (lat, lon)), sc["reach_km"],
                   prog(t, reveal + 0.2, sc.get("reach_dur", 2.5)), T["accent"])
    chrome(img, tg)
    text_a(img, (70, 300), f"#{sc['rank']}", F("anton", 150), T["alert"], clamp(t / 0.25), shadow=8)
    text_a(img, (76, 470), typed(sc.get("tag", ""), prog(t, 0.3, 0.6)), F("mono", 26), T["accent2"], 1)
    # card
    cy0 = 1070; ca = clamp((t - 0.2) / 0.3); dy = (1 - back((t - 0.2) / 0.5)) * 60
    rect_a(img, (50, cy0 + dy, W - 50, 1640 + dy), (8, 11, 9), 0.88 * ca, 26, T["land_edge"], 2)
    fl = flag(sc["code"], 210)
    if hide:
        paste_a(img, silhouette(fl), (80, cy0 + 40 + dy), ca)
        text_a(img, (80 + 105, cy0 + 40 + 95 + dy), "?", F("anton", 110), T["alert"], ca * (0.6 + 0.4 * pulse), "mm")
        text_a(img, (320, cy0 + 70 + dy), "IDENTIFYING", F("mono", 34), T["alert"], ca * (0.5 + 0.5 * (int(t * 4) % 2)))
        text_a(img, (320, cy0 + 120 + dy), "▒" * int(10 * prog(t, 0.3, reveal)), F("mono", 34), T["alert"], ca)
    else:
        r = t - reveal
        fla = clamp(r / 0.15); sc_ = 1 + 0.25 * (1 - ease(r / 0.4))
        f2 = fl.resize((int(fl.width * sc_), int(fl.height * sc_)), Image.BILINEAR)
        paste_a(img, f2, (80 + (fl.width - f2.width) / 2, cy0 + 40 + dy + (fl.height - f2.height) / 2), fla)
        name = sc["name"]; size = 96 if len(name) <= 9 else 70
        text_a(img, (320, cy0 + 50 + dy), typed(name, prog(t, reveal, 0.5)), F("disp", size, "Black"), WHITE, 1, shadow=5)
        text_a(img, (322, cy0 + 50 + size + 18 + dy), sc.get("sub", ""), F("inter", 32, "Medium"), MUTED, clamp(r / 0.4))
    # numbers
    na = clamp((t - reveal - 0.3) / 0.3)
    text_a(img, (90, 1325), sc.get("from_label", ""), F("inter", 34, "SemiBold"), MUTED, na)
    v0, v1 = sc["from"], sc["to"]; g2 = prog(t, reveal + 0.3, max(1.0, D * 0.3))
    cur = sc["to_label"] if g2 >= 0.999 else (sc.get("prefix", "") + f"{int(round(v0 + (v1 - v0) * g2)):,}")
    big_number(img, cur, 86, 1365, 148, T["accent"], na)
    tw = ImageDraw.Draw(img).textlength(cur, font=F("anton", 148))
    text_a(img, (100 + tw + 20, 1458), sc.get("unit", ""), F("disp", 44, "Black"), T["alert"], na)
    fa = clamp((t - reveal - 1.0) / 0.4)
    for i, ln in enumerate(sc.get("fact", [])):
        text_a(img, (90, 1566 + i * 42), typed(ln, prog(t, reveal + 1.0 + i * 0.6, 0.7)), F("inter", 36, "SemiBold"), T["accent2"], fa)
    # delta chip
    if sc.get("delta"):
        rect_a(img, (W - 330, 1355, W - 90, 1455), T["alert"], na * 0.95, 18)
        text_a(img, (W - 210, 1405), sc["delta"], F("anton", 64), WHITE, na, "mm")

def sc_bars(img, sc, t, D, tg, k):
    g = GLOBE.render(25, 70 + tg * 4, highlight=[r[0] for r in sc["rows"]], hl_alpha=0.8, dim_others=0.4, pulse=0.5)
    paste_a(img, g, (W / 2 - g.width / 2, 1250 - g.width / 2), 0.35)
    chrome(img, tg)
    text_a(img, (80, 320), sc["title"], F("disp", 88, "Black"), WHITE, clamp(t / 0.3), shadow=6)
    text_a(img, (84, 430), typed(sc.get("kicker", ""), prog(t, 0.2, 0.9)), F("mono", 28), T["accent2"], 1)
    mx = max(r[2] for r in sc["rows"])
    for i, (code, name, val, lab) in enumerate(sc["rows"]):
        st = 0.5 + i * (D * 0.5) / len(sc["rows"]); a = clamp((t - st) / 0.25); y = 540 + i * 210
        rect_a(img, (60, y, W - 60, y + 180), (8, 11, 9), a * 0.82, 18, T["alert"] if i == 0 else None, 2)
        paste_a(img, flag(code, 120), (90, y + 30), a)
        text_a(img, (240, y + 22), name, F("inter", 40, "SemiBold"), WHITE, a)
        bw = int(560 * val / mx * prog(t, st, 1.0)) + 8
        rect_a(img, (240, y + 100, 240 + bw, y + 146), T["alert"] if i == 0 else T["accent"], a, 8)
        text_a(img, (W - 90, y + 122), lab, F("anton", 70), WHITE, a, "rm")
    if sc.get("note"):
        text_a(img, (80, 540 + len(sc["rows"]) * 210 + 10), sc["note"], F("inter", 40, "SemiBold"), T["accent"], clamp((t - D * 0.7) / 0.4))


def roll_times(sc, D):
    """When each roll item reveals (scene-local seconds)."""
    n = len(sc["items"]); a = sc.get("first_at", 0.5); b = max(a + 0.1, D - sc.get("hold", 1.2))
    return [a + i * (b - a) / max(1, n - 1) if n > 1 else a for i in range(n)]

def sc_roll(img, sc, t, D, tg, k):
    """Rapid-fire countdown for short edits: the globe jumps to each country as its card pops into a stacked list."""
    items = sc["items"]; ts = roll_times(sc, D)
    cur = max([i for i, s in enumerate(ts) if t >= s - 0.35] or [0])
    la1, lo1 = CENTROID.get(items[cur][0], (20, 70)); la0, lo0 = CENTROID.get(items[max(0, cur - 1)][0], (la1, lo1))
    m = ease_io((t - (ts[cur] - 0.35)) / 0.45)
    dl = ((lo1 - lo0 + 180) % 360) - 180
    clat, clon = la0 + (la1 - la0) * m, lo0 + dl * m
    shown = [it[0] for i, it in enumerate(items) if t >= ts[i]]
    g = GLOBE.render(max(-45, min(45, clat)), clon, highlight=shown or None, hl_alpha=1, dim_others=0.35, pulse=0.5 + 0.5 * math.sin(tg * 6))
    paste_a(img, g, (W / 2 - g.width / 2, 640 - g.width / 2), 1)
    chrome(img, tg)
    text_a(img, (70, 300), sc.get("title", ""), F("disp", 64, "Black"), WHITE, clamp(t / 0.3), shadow=6)
    n = len(items); ch = min(124, int(620 / n)); y0 = 1660 - n * (ch + 8)
    for i, it in enumerate(items):
        code, name, num, chip = (list(it) + ["", ""])[:4]
        y = y0 + i * (ch + 8); r = t - ts[i]
        hid = r < 0
        a = clamp((t - 0.15 - i * 0.08) / 0.3)
        hot = i == cur and not hid
        rect_a(img, (50, y, W - 50, y + ch), (8, 11, 9), a * 0.9, 18, T["accent"] if hot else T["land_edge"], 3 if hot else 2)
        text_a(img, (80, y + ch / 2), f"#{sc.get('start_rank', n) - i}" if sc.get("ranked", True) else "", F("anton", 56), T["alert"], a, "lm")
        fl = flag(code, int(ch * 0.95))
        fx = 180
        if hid:
            paste_a(img, silhouette(fl), (fx, y + (ch - fl.height) / 2), a)
            text_a(img, (fx + fl.width / 2, y + ch / 2), "?", F("anton", int(ch * 0.6)), T["alert"], a, "mm")
            text_a(img, (fx + fl.width + 30, y + ch / 2), "▒▒▒▒▒▒", F("mono", 34), MUTED, a * 0.7, "lm")
            continue
        p = back(r / 0.35); s_ = 1 + 0.3 * (1 - ease(r / 0.35))
        f2 = fl.resize((int(fl.width * s_), int(fl.height * s_)), Image.BILINEAR)
        paste_a(img, f2, (fx + (fl.width - f2.width) / 2, y + (ch - f2.height) / 2), clamp(r / 0.12))
        text_a(img, (fx + fl.width + 30, y + ch / 2), typed(name, prog(t, ts[i], 0.3)), F("disp", 46, "Black"), WHITE, 1, "lm")
        text_a(img, (W - 90 - (190 if chip else 0), y + ch / 2), num, F("anton", 64), T["accent"], clamp(r / 0.25), "rm")
        if chip:
            rect_a(img, (W - 260, y + ch / 2 - 34, W - 80, y + ch / 2 + 34), T["alert"], clamp(r / 0.25) * 0.95, 14)
            text_a(img, (W - 170, y + ch / 2), chip, F("anton", 46), WHITE, clamp(r / 0.25), "mm")

def sc_outro(img, sc, t, D, tg, k):
    lon = 70 + t * 3
    g = GLOBE.render(20, lon, highlight=sc.get("highlight"), hl_alpha=0.9, dim_others=0.3, pulse=0.5 + 0.5 * math.sin(tg * 4))
    paste_a(img, g, (W / 2 - g.width / 2, 760 - g.width / 2), 0.9)
    chrome(img, tg)
    for i, (s, col) in enumerate(sc["lines"]):
        st = 0.4 + i * 0.7
        text_a(img, (80, 1010 + i * 92), typed(s, prog(t, st, 0.8)), F("disp", 70, "Black"), T[col] if col in T else WHITE, 1, shadow=6)
    st = sc.get("card_at", max(1.5, D - 4.0))
    a = clamp((t - st) / 0.35); p = back((t - st) / 0.5)
    rect_a(img, (60, 1350, W - 60, 1610), (255, 255, 255) if LIGHT else (14, 6, 26), a * 0.95, 30, T["accent"], 3)
    big = LOGO.resize((150, 150), Image.LANCZOS)
    paste_a(img, big, (95, 1415), a)
    text_a(img, (275, 1420), "UNKNOWN UNCOVERED", F("unb", 40, 800), WHITE, a)
    if sc.get("card") == "youtube":
        rect_a(img, (275, 1478, 275 + int(640 * clamp(p, 0, 1.08)), 1548), (230, 30, 40), a, 36)
        text_a(img, (300, 1513), "▶  FULL VIDEO ON YOUTUBE", F("disp", 38, "Black"), (255, 255, 255), clamp((t - st - 0.25) / 0.2), "lm")
        text_a(img, (279, 1560), "@Unknown_Uncovered_2026", F("inter", 30, "SemiBold"), T["accent"], clamp((t - st - 0.4) / 0.3))
        return
    rw = int(330 * clamp(p, 0, 1.15))
    rect_a(img, (275, 1490, 275 + rw, 1570), (230, 30, 40), a, 40)
    text_a(img, (300, 1530), "SUBSCRIBE", F("disp", 38, "Black"), (255, 255, 255), clamp((t - st - 0.25) / 0.2), "lm")
    rect_a(img, (625, 1490, 625 + int(330 * clamp(back((t - st - 0.3) / 0.5), 0, 1.15)), 1570), None, clamp((t - st - 0.3) / 0.3), 40, WHITE, 3)
    text_a(img, (655, 1530), "FOLLOW", F("disp", 38, "Black"), WHITE, clamp((t - st - 0.5) / 0.2), "lm")

SCENE_FN = {"hook": sc_hook, "tease": sc_tease, "stat": sc_stat, "rank": sc_rank, "bars": sc_bars, "outro": sc_outro, "roll": sc_roll}

# ---------------------------------------------------------------- timeline
DURS = json.load(open(os.path.join(WORK, "vo", "durs.json")))
LEAD, TAIL = SPEC.get("lead", 0.25), SPEC.get("tail", 0.35)
SCENES = []
for i, sc in enumerate(SPEC["scenes"]):
    d = max(sc.get("min", 3.0), DURS[i] + LEAD + TAIL + sc.get("extra", 0.0))
    SCENES.append((sc, round(d * FPS) / FPS))
STARTS = np.cumsum([0] + [d for _, d in SCENES]).tolist()

LOOK = SPEC.get("look", "")
_yy, _xx = np.mgrid[0:H, 0:W]
VIGNETTE = (1 - 0.5 * np.clip(((_xx - W / 2) / (W * 0.62)) ** 2 + ((_yy - H * 0.47) / (H * 0.6)) ** 2, 0, 1) ** 1.4)[..., None] if LOOK == "cinematic" else None
del _yy, _xx

_cap = {}
def caption_chunks(vo, maxc=20):
    """Split narration into short phrases (by words, ~maxc chars), breaking at punctuation."""
    out, cur = [], ""
    for w in vo.replace("—", " ").split():
        if cur and (len(cur) + 1 + len(w) > maxc): out.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
        if cur and cur[-1] in "।,?!:;": out.append(cur); cur = ""
    if cur: out.append(cur)
    return out

def draw_caption(img, sc, t, D):
    """Big Hindi caption for the phrase being spoken now (timed by character share of the narration)."""
    vo = sc.get("caption", sc.get("vo", ""))
    if not vo or sc.get("type") == "outro": return
    key = id(sc)
    if key not in _cap:
        ch = caption_chunks(vo); tot = sum(len(c) for c in ch); lead = SPEC.get("lead", 0.3)
        i = SPEC["scenes"].index(sc) if sc in SPEC["scenes"] else -1
        vd = DURS[i] if 0 <= i < len(DURS) else max(0.5, D - lead - SPEC.get("tail", 0.4)); acc = 0; times = []
        for c in ch: times.append((lead + acc / tot * vd, lead + (acc + len(c)) / tot * vd, c)); acc += len(c)
        _cap[key] = times
    for t0, t1, c in _cap[key]:
        if t0 <= t < t1 + 0.12:
            q = clamp((t - t0) / 0.12); y = SPEC.get("caption_y", 1440)
            s_ = c.rstrip("।,;:"); f = fit_font("hindi", 84, s_, W - 140)
            w = ImageDraw.Draw(img).textlength(s_, font=f)
            rect_a(img, (W / 2 - w / 2 - 36, y - 70, W / 2 + w / 2 + 36, y + 62), (0, 0, 0) if not LIGHT else (255, 255, 255), 0.62 * q, 26)
            text_a(img, (W / 2, y - 8 + 10 * (1 - q)), s_, f, (255, 232, 90) if not LIGHT else INK_CAP, q, "mm", shadow=6)
            break
INK_CAP = (22, 30, 40)

def frame(k, t, t0):
    sc, D = SCENES[k]; tg = t0 + t
    ox = 60 + 50 * math.sin(tg * 0.09); oy = 60 + 50 * math.cos(tg * 0.07)
    img = BG.crop((int(ox), int(oy), int(ox) + W, int(oy) + H))
    particles(img, tg)
    SCENE_FN[sc["type"]](img, sc, t, D, tg, k)
    if SPEC.get("captions"): draw_caption(img, sc, t, D)
    arr = np.asarray(img.convert("RGB")).astype(np.int16)
    gr = np.asarray(GRAIN[int(tg * FPS) % len(GRAIN)]).astype(np.int16) - 128
    arr += (gr * SPEC.get("grain", 0.06 if LIGHT else 0.18)).astype(np.int16)[..., None]
    if LOOK == "cinematic":
        L = arr.mean(axis=2, keepdims=True) / 255.0
        arr = arr + np.concatenate([(L - 0.5) * 26, (L - 0.5) * 6, (0.5 - L) * 22], axis=2).astype(np.int16)
        arr = (arr * VIGNETTE).astype(np.int16)
        g = max(0.0, 1 - t / 0.35) if k > 0 else 0.0     # soft warm light-wash cut
        if g > 0: arr = arr + (np.array([255, 190, 120]) * 0.55 * g ** 2).astype(np.int16)
        g = 0.0
    else:
        # transitions: whip flash + chromatic split at scene starts, fade at ends
        g = max(0.0, 1 - t / 0.25) if k > 0 else 0.0
    if g > 0:
        r = np.random.default_rng(int(tg * 1000))
        for _ in range(int(8 * g) + 1):
            y = int(r.uniform(0, H)); h = int(r.uniform(10, 90)); sh = int(r.uniform(-70, 70) * g)
            arr[y:y + h] = np.roll(arr[y:y + h], sh, axis=1)
        arr[..., 0] = np.roll(arr[..., 0], int(12 * g), axis=1); arr[..., 2] = np.roll(arr[..., 2], -int(12 * g), axis=1)
        if t < 2 / FPS: arr = arr + 90
    if k == 0 and t < 0.6 and not PUNCH: arr = (255 - (255 - arr) * (t / 0.6)) if LIGHT else arr * (t / 0.6)
    if k == len(SCENES) - 1 and D - t < 0.5: arr = arr * ((D - t) / 0.5)
    return np.clip(arr, 0, 255).astype(np.uint8)

def render_scene(k):
    sc, D = SCENES[k]; t0 = STARTS[k]
    name = f"{k:02d}_{sc['type']}"
    tmp, final = os.path.join(OUT, name + ".tmp.mp4"), os.path.join(OUT, name + ".mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", tmp],
                         stdin=subprocess.PIPE)
    for i in range(int(round(D * FPS))):
        p.stdin.write(frame(k, i / FPS, t0).tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, final)
    return name

def main():
    os.makedirs(OUT, exist_ok=True)
    mode = sys.argv[2]
    if mode == "still":
        ts = [float(x) for x in sys.argv[3].split(",")]
        for k, (sc, D) in enumerate(SCENES):
            for tt in ts:
                Image.fromarray(frame(k, min(tt, D - 0.1), STARTS[k])).save(os.path.join(OUT, f"still_{k:02d}_{sc['type']}_{tt}.png"))
    else:
        order = sorted(range(len(SCENES)), key=lambda k: -SCENES[k][1])
        with Pool(int(os.environ.get("UU_PROCS", "2"))) as pool: list(pool.imap_unordered(render_scene, order))
        with open(os.path.join(OUT, "list.txt"), "w") as fl:
            for k, (sc, _) in enumerate(SCENES): fl.write(f"file '{k:02d}_{sc['type']}.mp4'\n")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", os.path.join(OUT, "list.txt"),
                        "-c", "copy", os.path.join(OUT, "video_only.mp4")], check=True)
        print(json.dumps({"duration": STARTS[-1], "starts": STARTS}))

if __name__ == "__main__":
    main()
