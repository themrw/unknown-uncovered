"""Thumbnail background for reel 016: night refinery skyline under a globe with India + China lit."""
import sys, math, random
sys.argv = ["x", "/home/claude/work/016/spec.json"]
sys.path.insert(0, "/home/claude/unknown-uncovered/tools/v2")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import uu_render as R
W, H = 1080, 1920; S2 = 2
rnd = random.Random(4)
# sky
y = np.linspace(0, 1, H)[:, None]
top = np.array([8, 6, 10]); hor = np.array([120, 46, 10])
k = np.clip((y - 0.25) / 0.45, 0, 1) ** 1.6 * (1 - np.clip((y - 0.62) / 0.2, 0, 1))
sky = (top + (hor - top) * k[..., None]) * np.ones((1, W, 1))
bg = Image.fromarray(sky.astype(np.uint8)).convert("RGBA")
# globe, India + China lit
g = R.GLOBE.render(22, 92, highlight=["IN", "CN"], hl_alpha=1, dim_others=0.45, pulse=0.6)
gs = 640; g = g.resize((gs, gs), Image.LANCZOS)
bg.alpha_composite(g, (W // 2 - gs // 2, 470))
# refinery skyline (drawn at 2x)
L = Image.new("RGBA", (W * S2, H * S2), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
base = 1250 * S2; steel = (34, 27, 26, 255); edge = (255, 150, 60, 255)
lights = []
def column(x, w, h):
    d.rounded_rectangle([x, base - h, x + w, base], radius=w // 2, fill=steel, outline=edge, width=3)
    d.rounded_rectangle([x + 6, base - h + w // 2, x + 6 + w // 6, base - 6], radius=w // 12, fill=(150, 80, 40, 255))
    for j in range(1, 7):
        yy = base - h * j / 7; d.line([x - 10, yy, x + w + 10, yy], fill=(70, 50, 40, 255), width=6)
        lights.append((x + w + 10, yy)); lights.append((x - 10, yy))
    d.line([x + w * 0.5, base - h - 50, x + w * 0.5, base - h], fill=edge, width=5)
def flare(x, h):
    d.rectangle([x - 9, base - h, x + 9, base], fill=steel, outline=edge, width=2)
    return (x, base - h)
def sphere(cx, r):
    d.ellipse([cx - r, base - 2 * r - 20, cx + r, base - 20], fill=steel, outline=edge, width=3)
    for a in range(5): d.line([cx - r * 0.7 + a * r * 0.35, base - 20, cx - r * 0.7 + a * r * 0.35, base - r], fill=(70, 50, 40, 255), width=6)
def tank(x, w, h):
    d.rectangle([x, base - h, x + w, base], fill=steel, outline=edge, width=3)
    d.ellipse([x, base - h - 18, x + w, base - h + 18], fill=(40, 30, 28, 255), outline=edge, width=3)
cols = [(80, 70, 360), (200, 100, 600), (380, 70, 440), (560, 120, 720), (1460, 120, 760), (1640, 80, 500), (1800, 100, 640), (1960, 70, 400)]
tank(700, 220, 160); tank(1180, 240, 140)
for (x, w, h) in cols: column(x, w, h)
sphere(820, 120); sphere(1080, 100); sphere(1300, 120)
flares = [flare(330, 900), flare(1600, 960), flare(2050, 760)]
# pipe racks
for yy in (base - 120, base - 210):
    d.line([0, yy, W * S2, yy], fill=(60, 44, 36, 255), width=10)
d.rectangle([0, base, W * S2, H * S2], fill=(6, 5, 6, 255))
L = L.resize((W, H), Image.LANCZOS)
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
gd.ellipse([-200, 1050, W + 200, 1450], fill=(255, 120, 30, 120))
bg.alpha_composite(glow.filter(ImageFilter.GaussianBlur(90)))
bg.alpha_composite(L)
# lights + flames
fx = Image.new("RGBA", (W, H), (0, 0, 0, 0)); fd = ImageDraw.Draw(fx)
for (x, yy) in lights:
    if rnd.random() < 0.6:
        c = rnd.choice([(255, 210, 120), (255, 240, 200), (255, 160, 60)]); fd.ellipse([x / 2 - 3, yy / 2 - 3, x / 2 + 3, yy / 2 + 3], fill=c + (255,))
for (x, yy) in flares:
    x, yy = x / 2, yy / 2
    for (r, col) in ((60, (255, 90, 20, 140)), (38, (255, 150, 40, 220)), (20, (255, 230, 150, 255))):
        fd.ellipse([x - r * 0.55, yy - r * 2.0, x + r * 0.55, yy + 4], fill=col)
halo = fx.filter(ImageFilter.GaussianBlur(14))
bg.alpha_composite(halo); bg.alpha_composite(halo); bg.alpha_composite(fx)
# steam
st = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
for (x, w, h) in cols[1::3]:
    cx = (x + w / 2) / 2; cy = (base - h - 60) / 2
    for j in range(5): sd.ellipse([cx - 30 - j * 14, cy - 40 - j * 45, cx + 30 + j * 14, cy + 10 - j * 45], fill=(200, 170, 150, 40))
bg.alpha_composite(st.filter(ImageFilter.GaussianBlur(16)))
bg.convert("RGB").save("/home/claude/work/016/thumb_bg.jpg", quality=95); print("ok")
