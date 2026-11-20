"""Light thumbnail for reel 021 (Cipla): Hindi hook, India pill vs Big Pharma towers, price drop."""
import sys
out = sys.argv[1]; sys.argv = ["x", "/home/claude/work/021/spec.json"]
sys.path.insert(0, "/home/claude/unknown-uncovered/tools/v2")
from PIL import Image, ImageDraw, ImageFilter
import uu_story as S
R = S.R; W, H = R.W, R.H; F = R.F; text_a = R.text_a
INK = (22, 30, 40); TEAL = (0, 140, 130); SAFF = (240, 120, 20); GRN = (19, 136, 8); RED = (214, 48, 60)
img = R.BG.crop((60, 60, 60 + W, 60 + H)).copy()
# towers (Big Pharma), tilted, on the right
base = 1560
for i in range(5):
    x = 560 + i * 98; h = 520 + (i * 137) % 220
    lay = Image.new("RGBA", (120, h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rectangle([4, 10, 112, h + 19], fill=(84, 98, 118, 255)); d.rectangle([4, 10, 112, 40], fill=(62, 74, 92, 255))
    for r_ in range(int((h - 60) / 54)):
        for c in range(3): d.rectangle([18 + c * 32, 60 + r_ * 54, 36 + c * 32, 90 + r_ * 54], fill=(200, 216, 232, 255) if (r_ + c + i) % 4 else (255, 214, 120, 255))
    lay = lay.rotate(-6 - i * 1.5, center=(60, h + 20), resample=Image.BICUBIC)
    img.alpha_composite(lay, (x, base - h - 20))
R.rect_a(img, (600, 1180, 1040, 1260), (40, 50, 64), 0.95, 16); text_a(img, (820, 1220), "BIG PHARMA", F("anton", 60), (255, 255, 255), 1, "mm")
# the India pill, big, flying in
p = S.pill(460, 180, SAFF, GRN, band=(255, 255, 255)).rotate(18, expand=True, resample=Image.BICUBIC)
g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse([60, 1140, 620, 1560], fill=SAFF + (90,)); img.alpha_composite(g.filter(ImageFilter.GaussianBlur(60)))
img.alpha_composite(p, (80, 1230))
# impact burst
d = ImageDraw.Draw(img)
for k in range(10):
    import math
    a = math.radians(k * 36 + 10); d.line([560 + 60 * math.cos(a), 1330 + 60 * math.sin(a), 560 + 120 * math.cos(a), 1330 + 120 * math.sin(a)], fill=SAFF + (255,), width=10)
# hook
f = R.fit_font("hindi", 120, "भारत की एक गोली ने", W - 140)
text_a(img, (70, 250), "भारत की एक गोली ने", f, INK, 1, shadow=6)
f2 = R.fit_font("hindi", 120, "दवा कंपनियों को", W - 140)
text_a(img, (70, 410), "दवा कंपनियों को", f2, INK, 1, shadow=6)
text_a(img, (70, 570), "हरा दिया!", R.F("hindi", 150), SAFF, 1, shadow=6)
# price chips
S.card(img, (70, 800, 520, 1010), 1); text_a(img, (295, 860), "USA", F("disp", 36, "Black"), (120, 128, 136), 1, "mm")
text_a(img, (295, 945), "$10,400", F("anton", 96), (150, 158, 166), 1, "mm"); d = ImageDraw.Draw(img); d.line([120, 970, 470, 920], fill=RED + (255,), width=12)
S.card(img, (560, 800, 1010, 1010), 1, outline=TEAL); text_a(img, (785, 860), "INDIA", F("disp", 36, "Black"), TEAL, 1, "mm")
text_a(img, (785, 945), "$350", F("anton", 110), TEAL, 1, "mm")
st = "−96.6%"; R.rect_a(img, (380, 1030, 700, 1120), RED, 1, 40); text_a(img, (540, 1075), st, F("anton", 70), (255, 255, 255), 1, "mm")
R.paste_a(img, R.LOGO, (W - 70 - 92, 80), 1)
img.convert("RGB").save(out, quality=88); print(out)
