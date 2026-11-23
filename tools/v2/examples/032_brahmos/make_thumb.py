import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
sys.path.insert(0, "/home/claude/unknown-uncovered/tools/v2")
A = "/home/claude/unknown-uncovered/tools/v2/assets/"; M = "/home/claude/unknown-uncovered/media/032_asiapower/"; W, H = 1080, 1920
hi = lambda s: ImageFont.truetype(A + "Mukta-ExtraBold.ttf", s, layout_engine=ImageFont.Layout.RAQM)
an = lambda s: ImageFont.truetype(A + "Anton-Regular.ttf", s)
AM, GR = (255, 196, 92), (120, 225, 150)
EMOJI = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
def flag(code, w):
    s = "".join(chr(0x1F1E6 + ord(c) - 65) for c in code); im = Image.new("RGBA", (136, 128), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), s, font=EMOJI, embedded_color=True); return im.resize((w, int(w * 128 / 136)), Image.LANCZOS)
src = Image.open(M + "brahmos_4.jpg").convert("RGB"); s = max(W / src.width, H / src.height)
src = src.resize((int(src.width * s) + 1, int(src.height * s) + 1), Image.LANCZOS); x0 = int(src.width * 0.52 - W / 2); img = src.crop((x0, 0, x0 + W, H))
img = ImageEnhance.Contrast(ImageEnhance.Brightness(img).enhance(0.9)).enhance(1.1).convert("RGBA")
yy, xx = np.mgrid[0:H, 0:W]
g = np.zeros((H, W, 4), np.uint8); g[..., 3] = (np.clip(1 - yy / 950, 0, 1) ** 1.2 * 235 + np.clip((yy - 1300) / 620, 0, 1) * 225).astype(np.uint8); img.alpha_composite(Image.fromarray(g))
def txt(xy, s_, f, fill, stroke=8, anchor="mm"):
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((xy[0], xy[1] + 8), s_, font=f, fill=(0, 0, 0, 230), anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0, 230))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10))); ImageDraw.Draw(img).text(xy, s_, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0))
txt((W / 2, 230), "ब्रह्मोस ने बढ़ाई", hi(124), (255, 255, 255))
txt((W / 2, 400), "भारत की रैंकिंग!", hi(124), AM)
txt((W / 2, 640), "INDIA #3", an(220), AM, 10)
txt((W / 2, 810), "ASIA POWER INDEX 2026", an(66), (255, 255, 255), 6)
b = Image.new("RGBA", (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(b); bd.rounded_rectangle([110, 1540, W - 110, 1760], 26, fill=(8, 10, 14, 225), outline=(255, 255, 255, 160), width=3); img.alpha_composite(b)
ImageDraw.Draw(img).text((W / 2, 1590), "चीन के 3 पड़ोसी बने ख़रीदार", font=hi(56), fill=(255, 255, 255), anchor="mm")
for i, cc in enumerate(("PH", "VN", "ID")):
    f = flag(cc, 110); img.alpha_composite(f, (int(W / 2 - 200 + i * 145), 1640))
logo = Image.open(A + "logo_uu.png").convert("RGBA").resize((110, 110), Image.LANCZOS); img.alpha_composite(logo, (W - 150, 60))
img.convert("RGB").save("/home/claude/work/032/pub/thumbnail.jpg", quality=88); print("ok")
