import sys, math
sys.argv = ["x", "none"]
sys.path.insert(0, "/home/claude/reel4")
import render3 as R
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
MUK = "/home/claude/fonts/Mukta-ExtraBold.ttf"; ANT = "/home/claude/fonts/Anton-Regular.ttf"
def muk(s): return ImageFont.truetype(MUK, s, layout_engine=ImageFont.Layout.RAQM)
def ant(s): return ImageFont.truetype(ANT, s)
YEL = (255, 212, 0); RED = (232, 64, 70); WHITE = (255, 255, 255); BLACK = (8, 6, 8)

img = R.BG_BIG.crop((60, 60, 60 + W, 60 + H)).convert("RGBA")
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(glow).ellipse([90, 160, 990, 1060], fill=(230, 40, 40, 150))
img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(160)))
R.radar(img, W / 2, 610, 470, 1.3, 0.7)
d = ImageDraw.Draw(img)

def shadow_text(xy, s, f, fill, anchor="mm", sh=10, stroke=0):
    d.text((xy[0], xy[1] + sh), s, font=f, fill=BLACK, anchor=anchor, stroke_width=stroke, stroke_fill=BLACK)
    d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=BLACK)

# tag pill
d.rounded_rectangle([300, 215, 780, 290], 18, fill=RED)
d.text((540, 253), "SIPRI  2021 → 2026", font=ant(48), fill=WHITE, anchor="mm")

# radiation symbol with glow
sym = Image.new("RGBA", (W, 760), (0, 0, 0, 0))
ImageDraw.Draw(sym).text((540, 380), "☢", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 470), fill=YEL + (255,), anchor="mm")
g = sym.filter(ImageFilter.GaussianBlur(28))
img.alpha_composite(g, (0, 230)); img.alpha_composite(sym, (0, 230))
d = ImageDraw.Draw(img)

# headline
shadow_text((540, 1000), "चुपचाप", muk(190), YEL, stroke=6)
shadow_text((540, 1170), "परमाणु हथियार", muk(122), WHITE, stroke=5)
shadow_text((540, 1300), "कौन बढ़ा रहा है?", muk(112), WHITE, stroke=5)

# china stat
img.alpha_composite(R.flag("CN", 200), (70, 1385))
d = ImageDraw.Draw(img)
shadow_text((300, 1475), "350", ant(140), (210, 210, 215), anchor="lm", sh=7)
shadow_text((560, 1475), "→", ant(140), RED, anchor="lm", sh=7)
shadow_text((700, 1475), "620", ant(160), YEL, anchor="lm", sh=8)

# india sticker
st = Image.new("RGBA", (700, 150), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
sd.rounded_rectangle([0, 10, 690, 140], 26, fill=YEL)
st.alpha_composite(R.flag("IN", 130), (24, 14))
sd.text((180, 75), "भारत कहाँ?", font=muk(84), fill=BLACK, anchor="lm")
st = st.rotate(3, resample=Image.BICUBIC, expand=True)
sh = Image.new("RGBA", st.size, (0, 0, 0, 0)); sh.putalpha(st.getchannel("A").point(lambda v: int(v * 0.9)))
img.alpha_composite(Image.merge("RGBA", (Image.new("L", st.size, 0),) * 3 + (sh.getchannel("A"),)), (195, 1600))
img.alpha_composite(st, (190, 1588))

img.convert("RGB").save(sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] != "none" else "/home/claude/reel4/thumbnail.jpg", quality=88)
print("ok")
