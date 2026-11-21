from PIL import Image, ImageDraw, ImageFont, ImageFilter
A = "/home/claude/unknown-uncovered/tools/v2/assets/"; W, H = 1080, 1920
hi = lambda s: ImageFont.truetype(A + "Mukta-ExtraBold.ttf", s, layout_engine=ImageFont.Layout.RAQM)
an = lambda s: ImageFont.truetype(A + "Anton-Regular.ttf", s)
mono = lambda s: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", s)
NAVY, RED, GREEN, AMBER, INK = (16, 40, 92), (200, 30, 45), (14, 132, 78), (206, 132, 0), (22, 30, 44)
img = Image.new("RGBA", (W, H), (243, 244, 247, 255)); d = ImageDraw.Draw(img)
for y in range(0, H, 48):
    for x in range(0, W, 48): d.rectangle([x, y, x + 2, y + 2], fill=(222, 226, 234))
def card(box, out=None, r=26):
    x0, y0, x1, y1 = box; sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([x0, y0 + 14, x1, y1 + 14], r, fill=(30, 50, 80, 70)); img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
    ImageDraw.Draw(img).rounded_rectangle(box, r, fill=(255, 255, 255), outline=out or (220, 226, 234), width=3)
def stamp(txt, col, cx, cy, size=74, rot=-8):
    f = an(size); tw = d.textlength(txt, font=f); st = Image.new("RGBA", (int(tw) + 60, int(size * 1.5)), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
    sd.rounded_rectangle([4, 4, st.width - 4, st.height - 4], 12, outline=col + (255,), width=8); sd.text((st.width / 2, st.height / 2), txt, font=f, fill=col + (255,), anchor="mm")
    st = st.rotate(rot, expand=True, resample=Image.BICUBIC); img.alpha_composite(st, (int(cx - st.width / 2), int(cy - st.height / 2)))
d = ImageDraw.Draw(img)
d.rounded_rectangle([60, 250, 560, 350], 14, fill=RED); d.ellipse([88, 285, 118, 315], fill=(255, 255, 255)); d.text((140, 300), "REALITY CHECK", font=an(62), fill=(255, 255, 255), anchor="lm")
d.text((60, 400), "OFFICIAL DATA · VERIFIED SOURCES", font=mono(30), fill=(92, 102, 112), anchor="lm"); d.rectangle([60, 430, W - 60, 436], fill=NAVY)
d.text((W / 2, 545), "भारत की इकॉनमी", font=hi(124), fill=NAVY, anchor="mm")
d.text((W / 2, 690), "सच क्या है?", font=hi(140), fill=RED, anchor="mm")
rows = [("“DEAD ECONOMY”", "FALSE", RED), ("“ECONOMIC DISASTER”", "OVERSTATED", AMBER), ("“HERCULEAN FEAT”", "TRUE, BUT…", GREEN)]
for i, (q, v, c) in enumerate(rows):
    y = 880 + i * 200; card((70, y - 80, W - 70, y + 80)); d = ImageDraw.Draw(img); d.rounded_rectangle([70, y - 80, 88, y + 80], 6, fill=c)
    d.text((120, y), q, font=an(64 if i != 1 else 56), fill=INK, anchor="lm"); stamp(v, c, W - 230, y, 54 if len(v) > 6 else 66)
card((70, 1470, W - 70, 1690), NAVY); d = ImageDraw.Draw(img)
d.text((300, 1560), "7.8%", font=an(150), fill=GREEN, anchor="mm"); d.text((300, 1655), "GDP GROWTH", font=mono(30), fill=(92, 102, 112), anchor="mm")
d.line([W / 2 + 20, 1500, W / 2 + 20, 1660], fill=(220, 226, 234), width=4)
d.text((W - 290, 1560), "15.9%", font=an(150), fill=AMBER, anchor="mm"); d.text((W - 290, 1655), "YOUTH JOBLESS", font=mono(30), fill=(92, 102, 112), anchor="mm")
logo = Image.open(A + "logo_uu.png").convert("RGBA").resize((110, 110), Image.LANCZOS); img.alpha_composite(logo, (W - 170, 245))
img.convert("RGB").save("pub/thumbnail.jpg", quality=88); print("ok")
