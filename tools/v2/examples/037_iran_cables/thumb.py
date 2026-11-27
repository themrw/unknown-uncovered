import sys, os
OUT = sys.argv[1]; sys.argv = [sys.argv[0], "spec.json"]
sys.path.insert(0, "/home/claude/unknown-uncovered/tools/v2"); os.chdir("/home/claude/work/037")
from PIL import Image, ImageDraw, ImageEnhance
import uu_story as US, uu_render as R
W, H = 1080, 1920
bg = Image.open("media/037_cables/hormuz_0.jpg").convert("RGB"); s = max(W / bg.width, H / bg.height)
bg = bg.resize((int(bg.width * s), int(bg.height * s)), Image.LANCZOS); x0 = (bg.width - W) // 2; y0 = (bg.height - H) // 2
img = ImageEnhance.Brightness(bg.crop((x0, y0, x0 + W, y0 + H))).enhance(0.55).convert("RGBA")
g = Image.new("L", (1, H)); g.putdata([int(200 * max(0, 1 - y / 700) ** 1.5 + 120 * max(0, (y - 1400) / 520)) for y in range(H)])
sh = Image.new("RGBA", (W, H), (0, 0, 0, 255)); sh.putalpha(g.resize((W, H))); img.alpha_composite(sh)
A = (255, 196, 92)
def T(xy, s_, f, c, anc="mm", sh=14): US.text_a(img, xy, s_, f, c, 1.0, anc, shadow=sh)
T((W / 2, 260), "क्या ईरान", R.F("hindi", 120), (255, 255, 255))
T((W / 2, 410), "इंटरनेट बंद कर देगा?", R.F("hindi", 104), A)
T((W / 2, 900), "607", R.F("anton", 260), (255, 255, 255)); T((W / 2, 1040), "CABLE SYSTEMS WORLDWIDE", R.F("anton", 56), (220, 220, 215))
T((W / 2, 1220), "6", R.F("anton", 200), (255, 90, 70)); T((W / 2, 1340), "UNDER HORMUZ", R.F("anton", 56), (255, 150, 130))
st = Image.new("RGBA", (420, 124), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
sd.rounded_rectangle([0, 0, 419, 123], 26, fill=(220, 40, 40, 255)); sd.text((210, 60), "सच क्या है?", font=R.F("hindi", 74), fill=(255, 255, 255), anchor="mm")
st = st.rotate(-6, expand=True, resample=Image.BICUBIC); img.alpha_composite(st, (W - st.width - 50, 1480))
logo = Image.open("/home/claude/unknown-uncovered/tools/v2/assets/logo_uu.png").convert("RGBA"); logo.thumbnail((110, 110)); img.alpha_composite(logo, (W - 150, 50))
img.convert("RGB").save(OUT, quality=88)
