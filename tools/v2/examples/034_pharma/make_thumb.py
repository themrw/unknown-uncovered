import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
A = "/home/claude/unknown-uncovered/tools/v2/assets/"; M = "/home/claude/unknown-uncovered/media/034b_pharma/"; W, H = 1080, 1920
hi = lambda s: ImageFont.truetype(A + "Mukta-ExtraBold.ttf", s, layout_engine=ImageFont.Layout.RAQM)
an = lambda s: ImageFont.truetype(A + "Anton-Regular.ttf", s)
SAFF, CHN = (255, 153, 51), (235, 60, 60)
EMOJI = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
def flag(code, w):
    s = "".join(chr(0x1F1E6 + ord(c) - 65) for c in code); im = Image.new("RGBA", (136, 128), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), s, font=EMOJI, embedded_color=True); return im.resize((w, int(w * 128 / 136)), Image.LANCZOS)
src = Image.open(M + "tablets_0.jpg").convert("RGB"); s = max(W / src.width, H / src.height)
src = src.resize((int(src.width * s) + 1, int(src.height * s) + 1), Image.LANCZOS); x0 = (src.width - W) // 2; img = src.crop((x0, 0, x0 + W, H))
img = ImageEnhance.Brightness(img).enhance(0.55).convert("RGBA")
def txt(xy, s_, f, fill, stroke=8, anchor="mm"):
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((xy[0], xy[1] + 8), s_, font=f, fill=(0, 0, 0, 230), anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0, 230))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10))); ImageDraw.Draw(img).text(xy, s_, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0))
txt((W / 2, 260), "दुनिया की फ़ार्मेसी", hi(116), (255, 255, 255))
txt((W / 2, 400), "भारत है", hi(126), SAFF)
img.alpha_composite(flag("CN", 200), (W // 2 - 300, 560)); img.alpha_composite(flag("IN", 200), (W // 2 + 100, 560))
d = ImageDraw.Draw(img); d.polygon([(W / 2 + 70, 650), (W / 2 - 40, 590), (W / 2 - 40, 710)], fill=CHN)
txt((W / 2, 870), "पर कच्चा माल?", hi(110), (255, 255, 255))
txt((W / 2, 1080), "74%", an(300), CHN, 10)
txt((W / 2, 1250), "OF INDIA'S API IMPORTS FROM CHINA", an(54), (255, 255, 255), 5)
b = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(b).rounded_rectangle([90, 1560, W - 90, 1700], 24, fill=(160, 25, 25, 240), outline=(255, 255, 255, 220), width=3)
img.alpha_composite(b); ImageDraw.Draw(img).text((W / 2, 1630), "TB दवा का कच्चा माल: 100% चीन", font=hi(58), fill=(255, 255, 255), anchor="mm")
logo = Image.open(A + "logo_uu.png").convert("RGBA").resize((110, 110), Image.LANCZOS); img.alpha_composite(logo, (W - 150, 60))
img.convert("RGB").save("/home/claude/work/034/pub/thumbnail.jpg", quality=88); print("ok")
