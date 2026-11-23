import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
A = "/home/claude/unknown-uncovered/tools/v2/assets/"; M = "/home/claude/unknown-uncovered/media/031_tuvalu/"; W, H = 1080, 1920
hi = lambda s: ImageFont.truetype(A + "Mukta-ExtraBold.ttf", s, layout_engine=ImageFont.Layout.RAQM)
an = lambda s: ImageFont.truetype(A + "Anton-Regular.ttf", s)
AQ, CO = (110, 220, 235), (255, 128, 96)
src = Image.open(M + "funafuti_0.jpg").convert("RGB"); s = max(W / src.width, H / src.height)
src = src.resize((int(src.width * s) + 1, int(src.height * s) + 1), Image.LANCZOS); x0 = int(src.width * 0.50 - W / 2); img = src.crop((x0, 0, x0 + W, H))
img = ImageEnhance.Color(ImageEnhance.Brightness(img).enhance(0.85)).enhance(1.1).convert("RGBA")
yy, xx = np.mgrid[0:H, 0:W]
g = np.zeros((H, W, 4), np.uint8); g[..., 3] = (np.clip(1 - yy / 1100, 0, 1) ** 1.2 * 225 + np.clip((yy - 1350) / 570, 0, 1) * 210).astype(np.uint8); img.alpha_composite(Image.fromarray(g))
def txt(xy, s_, f, fill, stroke=8, anchor="mm"):
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((xy[0], xy[1] + 8), s_, font=f, fill=(0, 0, 0, 230), anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0, 230))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10))); ImageDraw.Draw(img).text(xy, s_, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0))
txt((W / 2, 250), "पूरा देश छोड़ने की", hi(108), (255, 255, 255))
txt((W / 2, 395), "लॉटरी!", hi(150), AQ)
txt((W / 2, 680), "82%", an(330), CO, 10)
txt((W / 2, 880), "SIGNED UP TO LEAVE", an(96), (255, 255, 255), 6)
b = Image.new("RGBA", (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(b)
bd.rounded_rectangle([220, 1590, W - 220, 1720], 22, fill=(10, 70, 90, 235), outline=(255, 255, 255, 200), width=3)
img.alpha_composite(b); ImageDraw.Draw(img).text((W / 2, 1652), "समुद्र में डूबता देश", font=hi(70), fill=(255, 255, 255), anchor="mm")
logo = Image.open(A + "logo_uu.png").convert("RGBA").resize((110, 110), Image.LANCZOS); img.alpha_composite(logo, (W - 150, 60))
img.convert("RGB").save("/home/claude/work/031/pub/thumbnail.jpg", quality=88); print("ok")
