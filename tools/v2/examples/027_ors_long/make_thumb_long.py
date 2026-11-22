import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
A = "/home/claude/unknown-uncovered/tools/v2/assets/"; M = "/home/claude/unknown-uncovered/media/026_ors/"; W, H = 1280, 720
hi = lambda s: ImageFont.truetype(A + "Mukta-ExtraBold.ttf", s, layout_engine=ImageFont.Layout.RAQM)
an = lambda s: ImageFont.truetype(A + "Anton-Regular.ttf", s)
src = Image.open(M + "refugees_2.jpg").convert("RGB"); s = max(W / src.width, H / src.height)
src = src.resize((int(src.width * s) + 1, int(src.height * s) + 1), Image.LANCZOS); img = src.crop((0, 0, W, H))
img = ImageOps.colorize(ImageOps.grayscale(img), (8, 28, 28), (220, 238, 232)).convert("RGBA")
xx = np.mgrid[0:H, 0:W][1]; g = np.clip((0.72 - xx / W) / 0.72, 0, 1) ** 0.8 * 0.92
lay = np.zeros((H, W, 4), np.uint8); lay[..., 3] = (g * 255).astype(np.uint8); img.alpha_composite(Image.fromarray(lay))
def txt(xy, s_, f, fill, anchor="lm", stroke=7):
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((xy[0], xy[1] + 6), s_, font=f, fill=(0, 0, 0, 200), anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0, 200))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6))); ImageDraw.Draw(img).text(xy, s_, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0))
txt((50, 110), "7 करोड़ जानें", hi(110), (255, 255, 255))
txt((50, 235), "बचाने वाला घोल", hi(96), (40, 230, 200))
txt((50, 360), "3 भारतीय डॉक्टरों की कहानी", hi(58), (255, 255, 255), stroke=5)
pk = Image.open(M + "packet_1.jpg").convert("RGBA"); pk.thumbnail((330, 330)); b = Image.new("RGBA", (pk.width + 18, pk.height + 18), (255, 255, 255, 255)); b.alpha_composite(pk, (9, 9))
b = b.rotate(-8, expand=True, resample=Image.BICUBIC); sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sh.alpha_composite(Image.new("RGBA", b.size, (0, 0, 0, 160)), (W - b.width - 50 + 12, 150 + 16))
img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14))); img.alpha_composite(b, (W - b.width - 50, 150))
st = Image.new("RGBA", (520, 110), (0, 0, 0, 0)); sd = ImageDraw.Draw(st); sd.rounded_rectangle([4, 4, 516, 106], 24, fill=(255, 214, 40), outline=(0, 0, 0), width=5)
sd.text((260, 53), "पहले हीरो को भूल गए!", font=hi(52), fill=(20, 20, 20), anchor="mm"); st = st.rotate(3, expand=True, resample=Image.BICUBIC); img.alpha_composite(st, (40, 440))
txt((52, 640), "ORS · THE INDIAN STORY", an(64), (40, 230, 200), stroke=4)
logo = Image.open(A + "logo_uu.png").convert("RGBA").resize((86, 86), Image.LANCZOS); img.alpha_composite(logo, (W - 120, 610))
img.convert("RGB").save("pub/thumbnail.jpg", quality=90); print("ok")
