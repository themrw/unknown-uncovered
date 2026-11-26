import sys, os
OUT = sys.argv[1]; sys.argv = [sys.argv[0], "spec.json"]
sys.path.insert(0, "/home/claude/unknown-uncovered/tools/v2"); os.chdir("/home/claude/work/036v2")
from PIL import Image, ImageDraw
import uu_story as US, uu_render as R
W, H = 1080, 1920
img = Image.new("RGBA", (W, H), (4, 6, 12, 255))
pr = US.m2_frame(img, 1, 1, {"punjab": 0.05, "up": 0.07, "bihar": 0.07, "delhi": 0.07, "meghalaya": 0.07}, ((81, 23.5), 1900, 0.6), ((81, 23.5), 1900, 0.6))
for k_, h in [("punjab", 150), ("delhi", 90), ("up", 120), ("bihar", 80), ("meghalaya", 140)]:
    (cx, cy), _, _ = US.MD_REG[k_]; x, y = pr(cx, cy); d = ImageDraw.Draw(img)
    d.line([(x, y), (x, y - h)], fill=(255, 210, 140, 230), width=4); d.ellipse([x - 9, y - 5, x + 9, y + 5], fill=(255, 196, 92, 255))
GOLD = (255, 196, 92)
def T(xy, s, f, c, anc="mm", sh=12): US.text_a(img, xy, s, f, c, 1.0, anc, shadow=sh)
T((W / 2, 250), "54 साल बाद…", R.F("hindi", 120), (255, 255, 255))
T((W / 2, 400), "अब बार-बार ब्लैकआउट?", R.F("hindi", 104), GOLD)
st = Image.new("RGBA", (500, 124), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
sd.rounded_rectangle([0, 0, 499, 123], 26, fill=(220, 40, 40, 255)); sd.text((250, 60), "आपके शहर में?", font=R.F("hindi", 72), fill=(255, 255, 255), anchor="mm")
st = st.rotate(-6, expand=True, resample=Image.BICUBIC); img.alpha_composite(st, (W - st.width - 40, 1420))
T((W / 2, 1690), "MOCK DRILLS · 2025–26", R.F("anton", 92), (255, 255, 255))
logo = Image.open("/home/claude/unknown-uncovered/tools/v2/assets/logo_uu.png").convert("RGBA"); logo.thumbnail((110, 110)); img.alpha_composite(logo, (W - 150, 50))
img.convert("RGB").save(OUT, quality=88)
