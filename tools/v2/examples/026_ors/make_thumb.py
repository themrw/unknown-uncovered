import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
A = "/home/claude/unknown-uncovered/tools/v2/assets/"; M = "/home/claude/unknown-uncovered/media/026_ors/"; W, H = 1080, 1920
hi = lambda s: ImageFont.truetype(A + "Mukta-ExtraBold.ttf", s, layout_engine=ImageFont.Layout.RAQM)
an = lambda s: ImageFont.truetype(A + "Anton-Regular.ttf", s)
src = Image.open(M + "refugees_2.jpg").convert("RGB"); s = max(W / src.width, H / src.height) * 1.05
src = src.resize((int(src.width * s), int(src.height * s)), Image.LANCZOS); x0 = (src.width - W) // 2; img = src.crop((x0, 0, x0 + W, H))
img = ImageOps.colorize(ImageOps.grayscale(img), (10, 30, 30), (225, 240, 235)).convert("RGBA")
yy = np.mgrid[0:H, 0:W][0]; g = np.clip((0.45 - yy / H) / 0.45, 0, 1) * 0.8 + np.clip((yy / H - 0.55) / 0.45, 0, 1) * 0.85
lay = np.zeros((H, W, 4), np.uint8); lay[..., 3] = (g * 255).astype(np.uint8); img.alpha_composite(Image.fromarray(lay))
def txt(xy, s_, f, fill, stroke=10):
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((xy[0], xy[1] + 10), s_, font=f, fill=(0, 0, 0, 200), anchor="mm", stroke_width=stroke, stroke_fill=(0, 0, 0, 200))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8))); ImageDraw.Draw(img).text(xy, s_, font=f, fill=fill, anchor="mm", stroke_width=stroke, stroke_fill=(0, 0, 0))
txt((W / 2, 330), "7 करोड़ जानें बचाने वाला घोल", hi(88), (255, 255, 255))
txt((W / 2, 490), "3 भारतीय डॉक्टरों की कहानी", hi(96), (40, 230, 200))
pk = Image.open(M + "packet_1.jpg").convert("RGBA"); pk.thumbnail((470, 470)); b = Image.new("RGBA", (pk.width + 24, pk.height + 24), (255, 255, 255, 255)); b.alpha_composite(pk, (12, 12))
b = b.rotate(-7, expand=True, resample=Image.BICUBIC); sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sh.alpha_composite(Image.new("RGBA", b.size, (0, 0, 0, 150)), (W // 2 - b.width // 2 + 14, 760 + 20))
img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18))); img.alpha_composite(b, (W // 2 - b.width // 2, 760))
st = Image.new("RGBA", (600, 140), (0, 0, 0, 0)); sd = ImageDraw.Draw(st); sd.rounded_rectangle([4, 4, 596, 136], 28, fill=(255, 214, 40), outline=(0, 0, 0), width=6)
sd.text((300, 68), "पहले हीरो को भूल गए!", font=hi(60), fill=(20, 20, 20), anchor="mm"); st = st.rotate(5, expand=True, resample=Image.BICUBIC); img.alpha_composite(st, (W - st.width - 30, 1300))
txt((W / 2, 1560), "ORS", an(230), (255, 255, 255), 12)
txt((W / 2, 1700), "THE INDIAN STORY", an(70), (40, 230, 200), 6)
logo = Image.open(A + "logo_uu.png").convert("RGBA").resize((110, 110), Image.LANCZOS); img.alpha_composite(logo, (W - 150, 60))
img.convert("RGB").save("pub/thumbnail.jpg", quality=88); print("ok")
