import sys, os, json
sys.argv = ["x", "/home/claude/work/011t/spec.json"]
sys.path.insert(0, "/home/claude/unknown-uncovered/tools/v2")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import uu_story as S
W, H = 1080, 1920
ph = Image.open("/home/claude/unknown-uncovered/media/011_passport/stamps_2.jpg").convert("RGB")
s = max(W / ph.width, H / ph.height) * 1.05
ph = ph.resize((int(ph.width * s), int(ph.height * s)), Image.LANCZOS)
ox, oy = (ph.width - W) // 2, (ph.height - H) // 2
bg = ph.crop((ox, oy, ox + W, oy + H))
bg = ImageEnhance.Color(bg).enhance(0.55); bg = ImageEnhance.Brightness(bg).enhance(0.42)
bg = Image.blend(bg, Image.new("RGB", (W, H), (40, 24, 10)), 0.35).filter(ImageFilter.GaussianBlur(2)).convert("RGBA")
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(glow).ellipse([60, 420, 900, 1320], fill=(255, 170, 70, 150))
bg.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
cv = S._cover("PASSPORT", "INTERNATIONAL TYPE · 1920")
cv = cv.resize((int(cv.width * 1.02), int(cv.height * 1.02)), Image.LANCZOS).rotate(-7, expand=True, resample=Image.BICUBIC)
x, y = 380 - cv.width // 2, 905 - cv.height // 2
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sh.alpha_composite(Image.new("RGBA", cv.size, (0, 0, 0, 200)), (x + 22, y + 30))
m = Image.new("L", (W, H), 0); m.paste(cv.getchannel("A"), (x + 22, y + 30)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(24)))
bg.alpha_composite(sh); bg.alpha_composite(cv, (x, y))
bg.convert("RGB").save("thumb_bg.jpg", quality=95)
