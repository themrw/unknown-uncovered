import numpy as np, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
A = "/home/claude/unknown-uncovered/tools/v2/assets/"; W, H = 1080, 1920
hi = lambda s: ImageFont.truetype(A + "Mukta-ExtraBold.ttf", s, layout_engine=ImageFont.Layout.RAQM)
an = lambda s: ImageFont.truetype(A + "Anton-Regular.ttf", s)
src = Image.open("/home/claude/unknown-uncovered/media/024_pits/rv_1.jpg").convert("RGB")
s = max(W / src.width, H / src.height) * 1.08; src = src.resize((int(src.width * s), int(src.height * s)), Image.LANCZOS)
x0 = (src.width - W) // 2; img = src.crop((x0, 0, x0 + W, H))
img = ImageEnhance.Contrast(ImageEnhance.Brightness(img).enhance(1.15)).enhance(1.15).convert("RGBA")
# red vignette + darken top/bottom for text
yy, xx = np.mgrid[0:H, 0:W]
e = np.clip(np.maximum(abs(xx - W / 2) / (W / 2), abs(yy - H / 2) / (H / 2)) - 0.45, 0, 1) / 0.55
lay = np.zeros((H, W, 4), np.uint8); lay[..., 0] = 200; lay[..., 1] = 20; lay[..., 2] = 20; lay[..., 3] = (e ** 1.5 * 200).astype(np.uint8)
img.alpha_composite(Image.fromarray(lay))
g = np.clip((0.42 - yy / H) / 0.42, 0, 1) * 0.75 + np.clip((yy / H - 0.62) / 0.38, 0, 1) * 0.85
lay = np.zeros((H, W, 4), np.uint8); lay[..., 3] = (g * 255).astype(np.uint8); img.alpha_composite(Image.fromarray(lay))
d = ImageDraw.Draw(img)
def txt(xy, s, f, fill, anchor="mm", stroke=10):
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((xy[0], xy[1] + 10), s, font=f, fill=(0, 0, 0, 220), anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0, 220))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    ImageDraw.Draw(img).text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0))
txt((W / 2, 330), "बम का 'दिल'", hi(170), (255, 255, 255))
txt((W / 2, 520), "फिर धड़कने लगा!", hi(150), (255, 70, 60))
# glowing plutonium core where the warheads converge
cx, cy, r = W / 2, 980, 150
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(glow).ellipse([cx - r * 1.8, cy - r * 1.8, cx + r * 1.8, cy + r * 1.8], fill=(255, 90, 30, 190))
img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(60)))
Y, X = np.mgrid[-r:r, -r:r].astype(np.float32) / r; rr = np.sqrt(X ** 2 + Y ** 2); z = np.sqrt(np.clip(1 - rr ** 2, 0, 1))
L = np.clip(-0.45 * X - 0.55 * Y + 0.7 * z, 0, 1); rim = np.clip((rr - 0.72) / 0.28, 0, 1)[..., None] ** 2 * np.array([255, 120, 40])
col = np.clip(np.stack([150 + 70 * L, 152 + 64 * L, 150 + 52 * L], -1) * (0.35 + 0.65 * L[..., None]) + rim * 0.9 + (L ** 18)[..., None] * 255, 0, 255)
sp = Image.fromarray(np.dstack([col, np.clip((1 - rr) * r / 1.5, 0, 1) * 255]).astype(np.uint8), "RGBA"); img.alpha_composite(sp, (int(cx - r), int(cy - r)))
# sticker
st = Image.new("RGBA", (470, 130), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
sd.rounded_rectangle([4, 4, 466, 126], 26, fill=(255, 214, 40), outline=(0, 0, 0), width=6); sd.text((235, 62), "37 साल बाद", font=hi(78), fill=(20, 20, 20), anchor="mm")
st = st.rotate(6, expand=True, resample=Image.BICUBIC); img.alpha_composite(st, (W - st.width - 40, 640))
txt((W / 2, 1380), "180", an(330), (255, 214, 40), stroke=12)
txt((W / 2, 1585), "BOMB CORES A YEAR", an(84), (255, 255, 255), stroke=6)
txt((W / 2, 1670), "U.S. TARGET BY 2050", an(56), (255, 120, 100), stroke=5)
logo = Image.open(A + "logo_uu.png").convert("RGBA").resize((110, 110), Image.LANCZOS); img.alpha_composite(logo, (W - 150, 60))
img.convert("RGB").save("pub/thumbnail.jpg", quality=88); print("ok")
