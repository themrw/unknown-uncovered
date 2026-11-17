#!/usr/bin/env python3
"""Premium "what they saw vs what happened" split thumbnail (1080x1920), for deception / reveal stories.

usage: uu_thumb_split.py spec.json out.jpg [variant]      (reads spec["thumb_split"], or spec["thumb_split"][variant] if it is a dict of variants)

thumb_split = {
  "chip": "POKHRAN · 11 MAY 1998",            # small saffron chip on top
  "title": ["INDIA FOOLED", "US INTELLIGENCE"], # huge gradient headline (Anton)
  "hook": "भारत ने CIA को चकमा दिया!",          # Hindi line under the panels (Mukta)
  "sticker": "कैसे?",
  "top": {"label": "WHAT THE CIA SAW", "status": "NO ACTIVITY"},       # green night-vision satellite panel
  "bottom": {"label": "WHAT HAPPENED", "status": "5 NUCLEAR TESTS"}     # orange desert blast panel
}
Key content stays inside the central 1080x1440 (y 240..1680).
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import uu_render as R          # reads sys.argv[1] (the spec) on import
import uu_story as S           # satellite drawing, brackets, dunes

W, H, T = R.W, R.H, R.T
cfg = R.SPEC["thumb_split"]
if len(sys.argv) > 3: cfg = cfg[sys.argv[3]]
out = sys.argv[2]
SAFF = (255, 170, 50); GREEN = (90, 255, 140); RED = (255, 60, 50)

def grad_text(img, xy, s, f, top, bot, stroke=10, glow=None, anchor="mm", pad=70):
    """Text filled with a vertical gradient, thin dark stroke, soft drop shadow and an optional coloured glow."""
    d = ImageDraw.Draw(img); x0, y0, x1, y1 = d.textbbox(xy, s, font=f, anchor=anchor, stroke_width=stroke)
    x0, y0 = int(math.floor(x0)) - pad, int(math.floor(y0)) - pad
    w, h = int(math.ceil(x1)) + pad - x0, int(math.ceil(y1)) + pad - y0
    p = (xy[0] - x0, xy[1] - y0)
    m = Image.new("L", (w, h)); ImageDraw.Draw(m).text(p, s, font=f, anchor=anchor, fill=255)
    ms = Image.new("L", (w, h)); ImageDraw.Draw(ms).text(p, s, font=f, anchor=anchor, fill=255, stroke_width=stroke)
    if glow:
        gl = Image.new("RGBA", (w, h), glow + (0,)); gl.putalpha(m.filter(ImageFilter.GaussianBlur(30)).point(lambda v: int(v * 0.65)))
        img.alpha_composite(gl, (x0, y0))
    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0)); sh.putalpha(m.point(lambda v: int(v * 0.85)))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)), (x0 + 5, y0 + 9))
    st = Image.new("RGBA", (w, h), (12, 8, 6, 0)); st.putalpha(ms); img.alpha_composite(st, (x0, y0))
    yy = np.linspace(0, 1, h)[:, None, None]
    g = (np.array(top) * (1 - yy) + np.array(bot) * yy) * np.ones((h, w, 1))
    fill = Image.fromarray(g.astype(np.uint8), "RGB").convert("RGBA"); fill.putalpha(m)
    img.alpha_composite(fill, (x0, y0))

def chip(img, cx, cy, s, f, bg, fg=(15, 10, 5)):
    d = ImageDraw.Draw(img); tw = d.textlength(s, font=f)
    R.rect_a(img, (cx - tw / 2 - 30, cy - 38, cx + tw / 2 + 30, cy + 38), bg, 1, 38)
    R.text_a(img, (cx, cy + 2), s, f, fg, 1, "mm")

# ------------------------------------------------------------ background: deep night
img = Image.new("RGBA", (W, H), (8, 7, 14, 255))
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(glow).ellipse([-200, 1250, W + 200, 2300], fill=(150, 70, 20, 120))
img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))

# ------------------------------------------------------------ panel 1: night-vision satellite view (what they saw)
PX0, PX1 = 60, W - 60
P1 = (PX0, 690, PX1, 1050); P2 = (PX0, 1075, PX1, 1435)
def panel_mask(box, r=28):
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).rounded_rectangle(box, r, fill=255); return m

nv = Image.new("RGBA", (W, H), (6, 26, 12, 255))
S.desert_ground(nv, 900, 3.0, 1.0, 0.0)
arr = np.asarray(nv.convert("RGB")).astype(np.float32)
lum = arr.mean(axis=2, keepdims=True)
arr = lum * np.array([0.35, 1.0, 0.45])[None, None, :] * 2.4 + np.array([4, 26, 10])
arr += np.random.default_rng(2).normal(0, 9, arr.shape[:2])[..., None]
arr[::4] *= 0.78                                                     # scan lines
nv = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
d = ImageDraw.Draw(nv)
cx, cy = W / 2 - 40, 900
S.brackets(d, (cx - 200, cy - 70, cx + 200, cy + 70), GREEN + (255,), 40, 6)
d.line([cx - 30, cy, cx + 30, cy], fill=GREEN + (200,), width=3); d.line([cx, cy - 30, cx, cy + 30], fill=GREEN + (200,), width=3)
S.draw_sat(d, W - 250, 790, 0.62, body=(150, 220, 160), panel=(40, 90, 60))
_bl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(_bl).polygon([(W - 250, 820), (cx - 200, cy + 70), (cx + 200, cy + 70)], fill=GREEN + (45,))
nv.alpha_composite(_bl.filter(ImageFilter.GaussianBlur(3))); d = ImageDraw.Draw(nv)
for i, s in enumerate(["SAT-PASS 11·05·98  03:14 UTC", "TARGET: POKHRAN 27.09N 71.75E"]):
    R.text_a(nv, (PX0 + 30, 712 + i * 32), s, R.F("mono", 24), GREEN, 0.9, shadow=0)
img.paste(nv, (0, 0), panel_mask(P1))

# ------------------------------------------------------------ panel 2: what happened (blast in the desert at dusk)
re = Image.new("RGBA", (W, H), (0, 0, 0, 255))
yy = np.linspace(0, 1, H)[:, None]
sky = np.array([30, 14, 30]) + (np.array([255, 120, 40]) - np.array([30, 14, 30])) * np.clip((yy * H - 1075) / 300, 0, 1) ** 1.3
re = Image.fromarray(np.repeat(sky[:, None, :], W, axis=1).reshape(H, W, 3).astype(np.uint8)).convert("RGBA")
lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
hy = 1380; top = 1120
dl.ellipse([W / 2 - 460, hy - 140, W / 2 + 460, hy + 120], fill=(255, 200, 90, 200))
for j in range(14):
    y = hy - 20 - (hy - 20 - top) * j / 13; rr = 54 + 14 * math.sin(j * 1.3) + 6 * j
    dl.ellipse([W / 2 - rr, y - rr * 0.8, W / 2 + rr, y + rr * 0.8], fill=(196, 128, 76, 245), outline=(120, 66, 40, 255), width=3)
cw = 300
for j in range(5):
    ox = (j - 2) * cw * 0.42; dl.ellipse([W / 2 + ox - cw * 0.55, top - cw * 0.35, W / 2 + ox + cw * 0.55, top + cw * 0.3], fill=(214, 146, 90, 245), outline=(130, 72, 44, 255), width=3)
re.alpha_composite(lay.filter(ImageFilter.GaussianBlur(3)))
core = Image.new("RGBA", (W, H), (0, 0, 0, 0)); cd = ImageDraw.Draw(core)
cd.ellipse([W / 2 - 150, hy - 70, W / 2 + 150, hy + 30], fill=(255, 250, 220, 255))
for j in range(5):
    ox = (j - 2) * cw * 0.42; cd.ellipse([W / 2 + ox - cw * 0.3, top - cw * 0.2, W / 2 + ox + cw * 0.3, top + cw * 0.1], fill=(255, 225, 170, 160))
re.alpha_composite(core.filter(ImageFilter.GaussianBlur(14)))
dn = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(dn)
for j, (yb, amp, col) in enumerate([(1360, 30, (70, 34, 20)), (1395, 26, (40, 20, 14))]):
    pts = [(x, yb + amp * math.sin(x / (210 + j * 70) + j * 2)) for x in range(0, W + 20, 12)]
    dd.polygon(pts + [(W, H), (0, H)], fill=col + (255,)); dd.line(pts, fill=(255, 190, 110, 160), width=3)
re.alpha_composite(dn)
img.paste(re, (0, 0), panel_mask(P2))

# panel frames + labels + status badges
d = ImageDraw.Draw(img)
d.rounded_rectangle(P1, 28, outline=GREEN + (230,), width=5)
d.rounded_rectangle(P2, 28, outline=SAFF + (255,), width=5)
def badge(img, x, y, s, bg, fg, size=58, tick=False):
    f = R.F("anton", size); dd = ImageDraw.Draw(img); tw = dd.textlength(s, font=f); pad = 70 if tick else 30
    R.rect_a(img, (x, y, x + tw + pad + 30, y + size + 34), bg, 0.95, 14)
    if tick:
        dd.line([x + 24, y + (size + 34) / 2, x + 40, y + (size + 34) / 2 + 16, x + 66, y + 18], fill=fg + (255,), width=9)
    R.text_a(img, (x + pad, y + (size + 34) / 2 + 2), s, f, fg, 1, "lm")
def label(img, x, y, s, col):
    R.text_a(img, (x, y), s, R.F("disp", 34, "Black"), col, 1, "lm", shadow=6)
label(img, PX0 + 30, 1012, cfg["top"]["label"], GREEN)
_f = R.F("anton", 58); _tw = d.textlength(cfg["top"]["status"], font=_f)
badge(img, PX1 - _tw - 130, 975, cfg["top"]["status"], (10, 40, 18), GREEN, 58, tick=True)
label(img, PX0 + 30, 1110, cfg["bottom"]["label"], (255, 236, 210))
st = cfg["bottom"]["status"]; f = R.F("anton", 66); tw = d.textlength(st, font=f)
badge(img, PX1 - tw - 90, 1330, st, RED, (255, 255, 255), 66)
# "VS" seal between the panels
R.rect_a(img, (W / 2 - 62, 1062 - 40, W / 2 + 62, 1062 + 40), (12, 10, 10), 1, 40, SAFF, 4)
R.text_a(img, (W / 2, 1064), "VS", R.F("anton", 52), SAFF, 1, "mm")

# ------------------------------------------------------------ headline block
R.paste_a(img, R.LOGO.resize((110, 110), Image.LANCZOS), (W - 70 - 110, 248), 1)
chip(img, 64 + 300, 300, cfg["chip"], R.F("mono", 34), SAFF)
t1, t2 = cfg["title"]
grad_text(img, (W / 2, 445), t1, R.fit_font("anton", 190, t1, W - 90), (255, 255, 255), (255, 222, 170), stroke=4, glow=(255, 120, 30))
grad_text(img, (W / 2, 600), t2, R.fit_font("anton", 150, t2, W - 90), (255, 206, 96), (255, 128, 28), stroke=4, glow=(255, 70, 10))

# ------------------------------------------------------------ Hindi hook + sticker
hk = cfg.get("hook", "")
if hk:
    R.text_a(img, (W / 2, 1530), hk, R.fit_font("hindi", 104, hk, W - 80), R.WHITE, 1, "mm", stroke=10, shadow=14)
if cfg.get("sticker"):
    f = R.F("hindi", 70); tw = ImageDraw.Draw(img).textlength(cfg["sticker"], font=f)
    stk = Image.new("RGBA", (int(tw) + 70, 120), (0, 0, 0, 0)); sd = ImageDraw.Draw(stk)
    sd.rounded_rectangle((4, 4, stk.width - 4, 116), 24, fill=RED + (255,), outline=(255, 255, 255, 255), width=5)
    sd.text((stk.width / 2, 64), cfg["sticker"], font=f, fill=(255, 255, 255), anchor="mm")
    stk = stk.rotate(8, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(stk, (W - stk.width - 40, 1600))

# cinematic finish: vignette + light grain
arr = np.asarray(img.convert("RGB")).astype(np.float32)
Y, X = np.mgrid[0:H, 0:W]
v = 1 - 0.45 * np.clip(((X - W / 2) / (W * 0.62)) ** 2 + ((Y - H * 0.5) / (H * 0.6)) ** 2, 0, 1) ** 1.4
arr = arr * v[..., None] + np.random.default_rng(9).normal(0, 4, arr.shape[:2])[..., None]
Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).save(out, "JPEG", quality=90, optimize=True)
print(out, os.path.getsize(out))
