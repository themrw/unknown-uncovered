import sys, os, json
OUT = sys.argv[1]; sys.argv = [sys.argv[0], "spec.json"]
sys.path.insert(0, "/home/claude/unknown-uncovered/tools/v2"); os.chdir("/home/claude/work/035")
from PIL import Image, ImageDraw
import uu_story as US, uu_render as R
W, H = 1080, 1920
img = Image.open("b3d/thumbp/size/0135.png").convert("RGBA").resize((W, H))
# slight push-in towards the pair
z = 1.0; cw, ch = W, H; x0 = 0; y0 = 0
img = img.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.LANCZOS)
an = json.load(open("b3d/thumbp/size/anchors.json"))["135"]
def tf(p): return ((p[0] - x0) * z, (p[1] - y0) * z)
US._vignette(img)
GOLD = (255, 200, 60)
def T(xy, s, f, c, anc="mm", sh=10): US.text_a(img, xy, s, f, c, 1.0, anc, shadow=sh)
T((W / 2, 250), "दुनिया का सारा सोना", R.F("hindi", 112), (255, 255, 255))
T((W / 2, 390), "एक क्यूब में?", R.F("hindi", 140), GOLD)
T((W / 2, 1440), "224,200 TONNES", R.F("anton", 120), (255, 255, 255))
x, y = tf(an["gate_top"]); US._tag(img, (x, y - 40), "INDIA GATE · 42 M", 44, (255, 225, 190))
p0, p1 = tf(an["cube_dim_b"]), tf(an["cube_dim_t"]); US._vline(img, p0, p1, 1.0); US._tag(img, (p0[0] - 30, (p0[1] + p1[1]) / 2), "22.6 M", 56, GOLD, 1.0, "rm")
st = Image.new("RGBA", (460, 124), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
sd.rounded_rectangle([0, 0, 459, 123], 26, fill=(220, 40, 40, 255)); sd.text((230, 60), "कितना बड़ा?", font=R.F("hindi", 74), fill=(255, 255, 255), anchor="mm")
st = st.rotate(-6, expand=True, resample=Image.BICUBIC); img.alpha_composite(st, (W - st.width - 60, 1560))
logo = Image.open("/home/claude/unknown-uncovered/tools/v2/assets/logo_uu.png").convert("RGBA"); logo.thumbnail((120, 120)); img.alpha_composite(logo, (W - 160, 60))
img.convert("RGB").save(OUT, quality=88)
