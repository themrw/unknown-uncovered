import sys, os
OUT = sys.argv[1]; sys.argv = [sys.argv[0], "spec.json"]
sys.path.insert(0, "/home/claude/unknown-uncovered/tools/v2"); os.chdir("/home/claude/work/038")
from PIL import Image, ImageDraw, ImageEnhance
import uu_story as US, uu_render as R
W, H = 1080, 1920
bg = Image.open("media/038_loc/metro_1.jpg").convert("RGB"); s = max(W / bg.width, H / bg.height)
bg = bg.resize((int(bg.width * s), int(bg.height * s)), Image.LANCZOS); x0 = (bg.width - W) // 2; y0 = (bg.height - H) // 2
img = ImageEnhance.Brightness(bg.crop((x0, y0, x0 + W, y0 + H))).enhance(0.55).convert("RGBA")
g = Image.new("L", (1, H)); g.putdata([int(200 * max(0, 1 - y / 700) ** 1.5 + 120 * max(0, (y - 1400) / 520)) for y in range(H)])
sh = Image.new("RGBA", (W, H), (0, 0, 0, 255)); sh.putalpha(g.resize((W, H))); img.alpha_composite(sh)
A = (255, 196, 92)
def T(xy, s_, f, c, anc="mm", sh=14): US.text_a(img, xy, s_, f, c, 1.0, anc, shadow=sh)
T((W / 2, 250), "भारत ने 68 देशों को", R.F("hindi", 100), (255, 255, 255))
T((W / 2, 390), "दिया कर्ज़!", R.F("hindi", 130), A)
T((W / 2, 900), "$32 BN", R.F("anton", 250), (255, 255, 255)); T((W / 2, 1040), "LINES OF CREDIT · MEA", R.F("anton", 56), (220, 220, 215))
T((W / 2, 1230), "#1 BANGLADESH", R.F("anton", 110), (255, 196, 92))
st = Image.new("RGBA", (520, 124), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
sd.rounded_rectangle([0, 0, 519, 123], 26, fill=(220, 40, 40, 255)); sd.text((260, 60), "75% वाली शर्त?", font=R.F("hindi", 74), fill=(255, 255, 255), anchor="mm")
st = st.rotate(-6, expand=True, resample=Image.BICUBIC); img.alpha_composite(st, (W - st.width - 50, 1480))
logo = Image.open("/home/claude/unknown-uncovered/tools/v2/assets/logo_uu.png").convert("RGBA"); logo.thumbnail((110, 110)); img.alpha_composite(logo, (W - 150, 50))
img.convert("RGB").save(OUT, quality=88)
