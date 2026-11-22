import numpy as np, math, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
sys.path.insert(0, "/home/claude/unknown-uncovered/tools/v2")
A = "/home/claude/unknown-uncovered/tools/v2/assets/"; M = "/home/claude/unknown-uncovered/media/029_nalist/"; W, H = 1080, 1920
hi = lambda s: ImageFont.truetype(A + "Mukta-ExtraBold.ttf", s, layout_engine=ImageFont.Layout.RAQM)
an = lambda s: ImageFont.truetype(A + "Anton-Regular.ttf", s)
mono = lambda s: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", s)
src = Image.open(M + "wagah_1.jpg").convert("RGB"); s = max(W / src.width, H / src.height)
src = src.resize((int(src.width * s) + 1, int(src.height * s) + 1), Image.LANCZOS); x0 = (src.width - W) // 2; img = src.crop((x0, 0, x0 + W, H))
img = ImageEnhance.Brightness(ImageEnhance.Color(img).enhance(0.6)).enhance(0.45).convert("RGBA")
yy, xx = np.mgrid[0:H, 0:W]
lay = np.zeros((H, W, 4), np.uint8); lay[..., 0] = 255; lay[..., 1] = 140; lay[..., 2] = 20; lay[..., 3] = (np.clip(1 - np.hypot(xx - W / 2, yy - 1050) / 700, 0, 1) ** 2 * 90).astype(np.uint8)
img.alpha_composite(Image.fromarray(lay))
def txt(xy, s_, f, fill, stroke=10, anchor="mm"):
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((xy[0], xy[1] + 10), s_, font=f, fill=(0, 0, 0, 220), anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0, 220))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8))); ImageDraw.Draw(img).text(xy, s_, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0))
txt((W / 2, 290), "दुश्मन को बताते हैं", hi(112), (255, 255, 255))
txt((W / 2, 440), "परमाणु ठिकानों का पता!", hi(108), (255, 205, 40))
# flags
def flag_img(code, w):
    from PIL import Image as I
    f = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
    s_ = "".join(chr(0x1F1E6 + ord(c) - 65) for c in code); t = I.new("RGBA", (160, 128), (0, 0, 0, 0))
    ImageDraw.Draw(t).text((0, 0), s_, font=f, embedded_color=True); t = t.crop(t.getbbox()); return t.resize((w, int(w * t.height / t.width)), I.LANCZOS)
fi, fp = flag_img("IN", 250), flag_img("PK", 250)
img.alpha_composite(fi, (50, 880)); img.alpha_composite(fp, (W - 300, 880))
# envelope
cx, cy, w, h = W / 2, 1020, 460, 300
env = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(env)
d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], 16, fill=(236, 226, 198), outline=(120, 100, 70), width=5)
d.line([cx - w / 2, cy - h / 2, cx, cy + 20, cx + w / 2, cy - h / 2], fill=(120, 100, 70), width=5)
d.ellipse([cx - 34, cy - 6, cx + 34, cy + 62], fill=(170, 30, 30)); d.text((cx, cy - 100), "TOP SECRET", font=an(46), fill=(170, 30, 30), anchor="mm")
d.text((cx, cy + 110), "LAT ██°██′  LONG ██°██′", font=mono(26), fill=(60, 50, 40), anchor="mm")
env = env.rotate(-6, center=(cx, cy), resample=Image.BICUBIC)
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([cx - w / 2 + 14, cy - h / 2 + 24, cx + w / 2 + 14, cy + h / 2 + 24], 16, fill=(0, 0, 0, 170))
img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18))); img.alpha_composite(env)
d = ImageDraw.Draw(img)
for k_, xs in ((1, (300, 400)), (-1, (W - 400, W - 300))):
    d.line([xs[0], 1020, xs[1], 1020], fill=(255, 205, 40), width=10)
st = Image.new("RGBA", (560, 130), (0, 0, 0, 0)); sd = ImageDraw.Draw(st); sd.rounded_rectangle([4, 4, 556, 126], 26, fill=(230, 40, 40), outline=(0, 0, 0), width=6)
sd.text((280, 62), "हर साल 1 जनवरी", font=hi(68), fill=(255, 255, 255), anchor="mm"); st = st.rotate(4, expand=True, resample=Image.BICUBIC); img.alpha_composite(st, (W // 2 - st.width // 2, 1250))
txt((W / 2, 1520), "35 YEARS", an(190), (255, 255, 255), 12)
txt((W / 2, 1665), "EVEN AFTER WARS", an(84), (255, 205, 40), 7)
logo = Image.open(A + "logo_uu.png").convert("RGBA").resize((110, 110), Image.LANCZOS); img.alpha_composite(logo, (W - 150, 60))
img.convert("RGB").save("pub/thumbnail.jpg", quality=88); print("ok")
