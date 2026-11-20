"""16:9 light thumbnail for the Cipla long video."""
import sys, math
out = sys.argv[1]; sys.argv = ["x", "/home/claude/work/022/spec.json"]
sys.path.insert(0, "/home/claude/unknown-uncovered/tools/v2")
from PIL import Image, ImageDraw, ImageFilter
import uu_lightlong as LL
R = LL.R; S = LL.S; W, H = R.W, R.H; F = R.F; text_a = R.text_a
INK, TEAL, SAFF, GRN, RED = LL.INK, LL.TEAL, LL.SAFF, LL.GRN, LL.RED
img = R.BG.crop((60, 60, 60 + W, 60 + H)).copy()
base = 1010
for i in range(6):
    x = 1080 + i * 128; h = 470 + (i * 137) % 260
    lay = Image.new("RGBA", (140, h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rectangle([5, 10, 132, h + 19], fill=(84, 98, 118, 255)); d.rectangle([5, 10, 132, 40], fill=(62, 74, 92, 255))
    for r_ in range(int((h - 60) / 54)):
        for c in range(3): d.rectangle([22 + c * 38, 60 + r_ * 54, 44 + c * 38, 90 + r_ * 54], fill=(200, 216, 232, 255) if (r_ + c + i) % 4 else (255, 214, 120, 255))
    lay = lay.rotate(-7 - i * 1.6, center=(70, h + 20), resample=Image.BICUBIC); img.alpha_composite(lay, (x, base - h - 20))
R.rect_a(img, (1200, 640, 1720, 730), (40, 50, 64), 0.95, 16); text_a(img, (1460, 685), "BIG PHARMA", F("anton", 68), (255, 255, 255), 1, "mm")
g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse([700, 620, 1260, 1020], fill=SAFF + (90,)); img.alpha_composite(g.filter(ImageFilter.GaussianBlur(60)))
p = S.pill(500, 190, SAFF, GRN, band=(255, 255, 255)).rotate(20, expand=True, resample=Image.BICUBIC); img.alpha_composite(p, (680, 690))
d = ImageDraw.Draw(img)
for k in range(10):
    a = math.radians(k * 36 + 10); d.line([1160 + 60 * math.cos(a), 800 + 60 * math.sin(a), 1160 + 130 * math.cos(a), 800 + 130 * math.sin(a)], fill=SAFF + (255,), width=12)
text_a(img, (80, 110), "एक भारतीय कंपनी ने", R.fit_font("hindi", 120, "एक भारतीय कंपनी ने", 1100), INK, 1, shadow=6)
text_a(img, (80, 270), "Big Pharma को हराया!", R.fit_font("hindi", 130, "Big Pharma को हराया!", 1150), SAFF, 1, shadow=6)
S.card(img, (80, 520, 560, 740), 1); text_a(img, (320, 575), "AIDS MEDICINE · 2000", F("disp", 30, "Black"), (120, 128, 136), 1, "mm")
text_a(img, (320, 665), "$10,000", F("anton", 110), (150, 158, 166), 1, "mm"); d = ImageDraw.Draw(img); d.line([120, 700, 520, 640], fill=RED + (255,), width=14)
S.card(img, (80, 780, 560, 1000), 1, outline=TEAL); text_a(img, (320, 835), "CIPLA · 2001", F("disp", 30, "Black"), TEAL, 1, "mm")
text_a(img, (320, 925), "$1 / DAY", F("anton", 110), TEAL, 1, "mm")
R.paste_a(img, R.LOGO.resize((110, 110), Image.LANCZOS), (W - 150, 40), 1)
img.convert("RGB").resize((1280, 720), Image.LANCZOS).save(out, quality=90); print(out)
