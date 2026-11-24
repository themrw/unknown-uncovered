import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
A = "/home/claude/unknown-uncovered/tools/v2/assets/"; M = "/home/claude/unknown-uncovered/media/"; W, H = 1280, 720
hi = lambda s: ImageFont.truetype(A + "Mukta-ExtraBold.ttf", s, layout_engine=ImageFont.Layout.RAQM)
an = lambda s: ImageFont.truetype(A + "Anton-Regular.ttf", s)
AM = (255, 196, 92)
EMOJI = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
def flag(code, w):
    s = "".join(chr(0x1F1E6 + ord(c) - 65) for c in code); im = Image.new("RGBA", (136, 128), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), s, font=EMOJI, embedded_color=True); return im.resize((w, int(w * 128 / 136)), Image.LANCZOS)
src = Image.open(M + "033_nalong/wagah_0.jpg").convert("RGB"); s = max(W / src.width, H / src.height)
src = src.resize((int(src.width * s) + 1, int(src.height * s) + 1), Image.LANCZOS); img = src.crop((0, 0, W, H))
img = ImageEnhance.Brightness(img).enhance(0.8).convert("RGBA")
yy, xx = np.mgrid[0:H, 0:W]
g = np.zeros((H, W, 4), np.uint8); g[..., 3] = (np.clip(1 - xx / 900, 0, 1) ** 0.9 * 235).astype(np.uint8); img.alpha_composite(Image.fromarray(g))
def txt(xy, s_, f, fill, stroke=6, anchor="lm"):
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((xy[0], xy[1] + 6), s_, font=f, fill=(0, 0, 0, 230), anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0, 230))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8))); ImageDraw.Draw(img).text(xy, s_, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0))
txt((50, 95), "दुश्मन को दी", hi(84), (255, 255, 255))
txt((50, 205), "परमाणु ठिकानों", hi(96), AM)
txt((50, 315), "की लिस्ट!", hi(96), AM)
txt((50, 470), "35 TIMES", an(130), (255, 255, 255), 6)
txt((54, 565), "NEVER MISSED · EVEN IN WAR", an(46), (255, 255, 255), 4)
fi = flag("IN", 150); fp = flag("PK", 150)
img.alpha_composite(fi, (W - 380, 470)); img.alpha_composite(fp, (W - 200, 470))
b = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(b).rounded_rectangle([W - 400, 360, W - 40, 450], 18, fill=(170, 25, 25, 240), outline=(255, 255, 255, 220), width=3)
img.alpha_composite(b); ImageDraw.Draw(img).text((W - 220, 403), "हर 1 जनवरी!", font=hi(56), fill=(255, 255, 255), anchor="mm")
logo = Image.open(A + "logo_uu.png").convert("RGBA").resize((80, 80), Image.LANCZOS); img.alpha_composite(logo, (W - 110, 28))
img.convert("RGB").save("/home/claude/work/033/pub/thumbnail.jpg", quality=90); print("ok")
