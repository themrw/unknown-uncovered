import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
A = "/home/claude/unknown-uncovered/tools/v2/assets/"; M = "/home/claude/unknown-uncovered/media/028_iaf/"; W, H = 1080, 1920
hi = lambda s: ImageFont.truetype(A + "Mukta-ExtraBold.ttf", s, layout_engine=ImageFont.Layout.RAQM)
an = lambda s: ImageFont.truetype(A + "Anton-Regular.ttf", s)
src = Image.open(M + "rafale_1.jpg").convert("RGB"); s = max(W / src.width, H / src.height) * 1.02
src = src.resize((int(src.width * s), int(src.height * s)), Image.LANCZOS); x0 = (src.width - W) // 2 + 60; img = src.crop((x0, 0, x0 + W, H))
img = ImageEnhance.Color(ImageEnhance.Contrast(img).enhance(1.2)).enhance(0.7).convert("RGBA")
yy, xx = np.mgrid[0:H, 0:W]
e = np.clip(np.maximum(abs(xx - W / 2) / (W / 2), abs(yy - H / 2) / (H / 2)) - 0.4, 0, 1) / 0.6
lay = np.zeros((H, W, 4), np.uint8); lay[..., 0] = 170; lay[..., 1] = 10; lay[..., 2] = 10; lay[..., 3] = (e ** 1.4 * 210).astype(np.uint8); img.alpha_composite(Image.fromarray(lay))
g = np.clip((0.4 - yy / H) / 0.4, 0, 1) * 0.85 + np.clip((yy / H - 0.6) / 0.4, 0, 1) * 0.9
lay = np.zeros((H, W, 4), np.uint8); lay[..., 3] = (g * 255).astype(np.uint8); img.alpha_composite(Image.fromarray(lay))
def txt(xy, s_, f, fill, stroke=10):
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((xy[0], xy[1] + 10), s_, font=f, fill=(0, 0, 0, 210), anchor="mm", stroke_width=stroke, stroke_fill=(0, 0, 0, 210))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8))); ImageDraw.Draw(img).text(xy, s_, font=f, fill=fill, anchor="mm", stroke_width=stroke, stroke_fill=(0, 0, 0))
txt((W / 2, 300), "चीन सीमा पर", hi(120), (255, 255, 255))
txt((W / 2, 450), "क्यों गरजे जेट?", hi(140), (255, 70, 60))
st = Image.new("RGBA", (640, 130), (0, 0, 0, 0)); sd = ImageDraw.Draw(st); sd.rounded_rectangle([4, 4, 636, 126], 26, fill=(255, 214, 40), outline=(0, 0, 0), width=6)
sd.text((320, 63), "चंडीगढ़ से LAC तक", font=hi(70), fill=(20, 20, 20), anchor="mm"); st = st.rotate(-4, expand=True, resample=Image.BICUBIC); img.alpha_composite(st, (W // 2 - st.width // 2, 560))
txt((W / 2, 1450), "9 DAYS", an(200), (255, 255, 255), 12)
txt((W / 2, 1600), "SUKHOI · RAFALE · TEJAS", an(72), (255, 200, 60), 6)
txt((W / 2, 1690), "क्या कुछ बड़ा होने वाला है?", hi(58), (255, 255, 255), 6)
logo = Image.open(A + "logo_uu.png").convert("RGBA").resize((110, 110), Image.LANCZOS); img.alpha_composite(logo, (W - 150, 60))
img.convert("RGB").save("pub/thumbnail.jpg", quality=88); print("ok")
