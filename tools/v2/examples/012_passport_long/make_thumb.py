"""Custom 1280x720 thumbnail for reel 012 (passport documentary). usage: make_thumb.py spec.json out.jpg"""
import sys, os
out = sys.argv[2]; sys.argv = sys.argv[:2]
sys.path.insert(0, "/home/claude/unknown-uncovered/tools/v2")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import uu_render as R, uu_story as S
W, H = 1920, 1080
ph = Image.open("/home/claude/unknown-uncovered/media/011_passport/stamps_2.jpg").convert("RGB")
s = max(W / ph.width, H / ph.height); ph = ph.resize((int(ph.width * s), int(ph.height * s)), Image.LANCZOS)
ph = ph.crop(((ph.width - W) // 2, (ph.height - H) // 2, (ph.width - W) // 2 + W, (ph.height - H) // 2 + H))
ph = ImageEnhance.Color(ph).enhance(0.5); ph = ImageEnhance.Brightness(ph).enhance(0.35)
img = Image.blend(ph, Image.new("RGB", (W, H), (36, 22, 10)), 0.35).filter(ImageFilter.GaussianBlur(3)).convert("RGBA")
x = np.linspace(0, 1, W)[None, :]; a = np.clip(1 - x / 0.62, 0, 1) ** 1.2 * 0.85
lay = np.zeros((H, W, 4), np.uint8); lay[..., 3] = (np.tile(a, (H, 1)) * 255).astype(np.uint8); img.alpha_composite(Image.fromarray(lay))
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(glow).ellipse([1100, 80, 1900, 1050], fill=(255, 170, 70, 150))
img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(130)))
cv = S._cover("PASSPORT", "INTERNATIONAL TYPE · 1920"); cv = cv.resize((int(cv.width * 1.55), int(cv.height * 1.55)), Image.LANCZOS)
st = S.stamp_img("TEMPORARY", size=100); st = st.resize((int(st.width * 1.15), int(st.height * 1.15)), Image.LANCZOS).rotate(14, expand=True, resample=Image.BICUBIC)
cv.alpha_composite(st, ((cv.width - st.width) // 2, int(cv.height * 0.56 - st.height / 2)))
cv = cv.rotate(-8, expand=True, resample=Image.BICUBIC)
px, py = 1500 - cv.width // 2, 540 - cv.height // 2
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); m = Image.new("L", (W, H), 0); m.paste(cv.getchannel("A"), (px + 26, py + 34))
sh.putalpha(m.filter(ImageFilter.GaussianBlur(26)).point(lambda v: v * 3 // 4)); img.alpha_composite(sh); img.alpha_composite(cv, (px, py))
R.text_a(img, (80, 120), "पासपोर्ट", R.F("hindi", 230), R.WHITE, 1, stroke=12, shadow=18)
R.text_a(img, (84, 420), "एक 'अस्थायी'", R.F("hindi", 150), R.T["accent"], 1, stroke=10, shadow=16)
R.text_a(img, (84, 620), "नियम था!", R.F("hindi", 150), R.T["accent"], 1, stroke=10, shadow=16)
f = R.F("anton", 84); lab = "1414 → 2026"; tw = ImageDraw.Draw(img).textlength(lab, font=f)
R.rect_a(img, (84, 880, 84 + tw + 70, 1000), R.T["alert"], 0.95, 22)
R.text_a(img, (84 + 35 + tw / 2, 940), lab, f, R.WHITE, 1, "mm")
R.paste_a(img, R.LOGO.resize((120, 120), Image.LANCZOS), (W - 160, 40), 1)
img.convert("RGB").resize((1280, 720), Image.LANCZOS).save(out, quality=90)
print(out, os.path.getsize(out))
