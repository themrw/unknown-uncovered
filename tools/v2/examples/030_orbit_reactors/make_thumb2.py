import numpy as np, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
A = "/home/claude/unknown-uncovered/tools/v2/assets/"; M = "/home/claude/unknown-uncovered/media/030b_orbit/"; W, H = 1080, 1920
hi = lambda s: ImageFont.truetype(A + "Mukta-ExtraBold.ttf", s, layout_engine=ImageFont.Layout.RAQM)
an = lambda s: ImageFont.truetype(A + "Anton-Regular.ttf", s)
AM = (255, 196, 92)
src = Image.open(M + "nightsky_1.jpg").convert("RGB"); s = max(W / src.width, H / src.height)
src = src.resize((int(src.width * s) + 1, int(src.height * s) + 1), Image.LANCZOS); x0 = int(src.width * 0.42 - W / 2); img = src.crop((x0, 0, x0 + W, H))
img = ImageEnhance.Color(ImageEnhance.Brightness(img).enhance(0.8)).enhance(0.8).convert("RGBA")
yy, xx = np.mgrid[0:H, 0:W]
g = np.zeros((H, W, 4), np.uint8); g[..., 3] = (np.clip(1 - yy / 1000, 0, 1) ** 1.3 * 210 + np.clip((yy - 1400) / 520, 0, 1) * 200).astype(np.uint8); img.alpha_composite(Image.fromarray(g))
v = (np.clip(((xx - W / 2) / (W * 0.65)) ** 2 + ((yy - H / 2) / (H * 0.65)) ** 2, 0, 1) * 160).astype(np.uint8); vv = np.zeros((H, W, 4), np.uint8); vv[..., 3] = v; img.alpha_composite(Image.fromarray(vv))
def glow(x, y, r, col, a=1.0):
    gg = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gg).ellipse([x - r * 3, y - r * 3, x + r * 3, y + r * 3], fill=col + (int(140 * a),))
    img.alpha_composite(gg.filter(ImageFilter.GaussianBlur(r * 1.3))); ImageDraw.Draw(img).ellipse([x - r, y - r, x + r, y + r], fill=(255, 248, 225, 255))
# satellites with short trails
d = ImageDraw.Draw(img)
for (x, y) in ((150, 1010), (420, 960), (760, 1060), (940, 980), (300, 1180), (640, 1150)):
    for q in range(14): d.line([x - (q + 1) * 10, y - (q + 1) * 2, x - q * 10, y - q * 2], fill=AM + (int(150 * (1 - q / 14)),), width=3)
    glow(x, y, 7, AM)
# the falling one: fireball streak
lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay); x0_, y0_, x1_, y1_ = 560, 1000, 860, 1500
for m in range(60):
    f = m / 60; px, py = x1_ - (x1_ - x0_) * f, y1_ - (y1_ - y0_) * f; r_ = 26 * (1 - f) + 3
    ld.ellipse([px - r_, py - r_, px + r_, py + r_], fill=(255, int(170 - 100 * f), 60, int(230 * (1 - f))))
img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(5))); img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(1.5))); glow(x1_, y1_, 16, (255, 130, 50))
def txt(xy, s_, f, fill, stroke=8, anchor="mm"):
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((xy[0], xy[1] + 8), s_, font=f, fill=(0, 0, 0, 230), anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0, 230))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10))); ImageDraw.Draw(img).text(xy, s_, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0))
txt((W / 2, 270), "आपके सिर के ऊपर", hi(116), (255, 255, 255))
txt((W / 2, 520), "30+", an(300), AM, 10)
txt((W / 2, 730), "NUCLEAR REACTORS", an(118), (255, 255, 255), 8)
# understated badge
b = Image.new("RGBA", (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(b)
bd.rounded_rectangle([170, 1590, W - 170, 1720], 22, fill=(150, 20, 20, 235), outline=(255, 255, 255, 200), width=3)
img.alpha_composite(b); ImageDraw.Draw(img).text((W / 2, 1652), "एक गिर भी चुका है", font=hi(74), fill=(255, 255, 255), anchor="mm")
logo = Image.open(A + "logo_uu.png").convert("RGBA").resize((110, 110), Image.LANCZOS); img.alpha_composite(logo, (W - 150, 60))
img.convert("RGB").save("/home/claude/work/030/pub/thumbnail.jpg", quality=88); print("ok")
