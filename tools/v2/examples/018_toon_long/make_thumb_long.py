"""16:9 thumbnail for long video 018: cartoon Haque & Bose (illustration), glowing fingerprint, proud hook."""
import sys
out = sys.argv[1]; sys.argv = ["x", "/home/claude/work/018/spec.json"]
sys.path.insert(0, "/home/claude/unknown-uncovered/tools/v2")
from PIL import Image, ImageDraw, ImageFilter
import uu_toon as TN, uu_long as L, uu_story as S
R = L.R; W, H, T = R.W, R.H, R.T
img = TN.get_set("finale").copy()
img.alpha_composite(Image.new("RGBA", (W, H), (20, 8, 0, 90)))
g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse([1050, 80, 1950, 980], fill=(255, 200, 110, 170))
img.alpha_composite(g.filter(ImageFilter.GaussianBlur(120)))
fp = S.fp_img(560, 700, 11, (255, 220, 140), 0.9)
glo = fp.filter(ImageFilter.GaussianBlur(18)); img.alpha_composite(glo, (1180, 120)); img.alpha_composite(fp, (1180, 120))
for i, (who, x, face) in enumerate((("haque", 1280, 1), ("bose", 1680, -1))):
    b = TN.person(who, 0.5, None, False, "down", blink_seed=1.0)
    if face < 0: b = b.transpose(Image.FLIP_LEFT_RIGHT)
    b = b.resize((int(b.width * 1.15), int(b.height * 1.15)), Image.LANCZOS)
    img.alpha_composite(b, (int(x - b.width / 2), H - b.height + 40))
L.gradient(img, "left", 0.92, 0.55)
hook = [("दुनिया की पुलिस का", (245, 245, 240)), ("सिस्टम", (245, 245, 240)), ("2 भारतीयों ने बनाया!", T["accent"])]
ys = [70, 230, 400]
for (s, col), y in zip(hook, ys):
    f = R.fit_font("hindi", 140, s, 1050); R.text_a(img, (80, y), s, f, col, 1, shadow=14)
R.text_a(img, (86, 620), "FINGERPRINT", R.F("anton", 150), (255, 255, 255), 1, shadow=14)
R.text_a(img, (92, 800), "CALCUTTA · 1897", R.F("disp", 60, "Black"), T["accent2"] if "accent2" in T else (200, 220, 230), 1, shadow=8)
st = "100 साल का राज़"; f = R.F("hindi", 62); w = ImageDraw.Draw(img).textlength(st, font=f)
lay = Image.new("RGBA", (int(w + 80), 120), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
ld.rounded_rectangle([0, 0, w + 79, 119], 26, fill=(220, 40, 40, 255), outline=(255, 255, 255, 255), width=5)
ld.text((w / 2 + 40, 58), st, font=f, fill=(255, 255, 255, 255), anchor="mm"); lay = lay.rotate(4, expand=True, resample=Image.BICUBIC)
img.alpha_composite(lay, (90, 900))
R.paste_a(img, R.LOGO, (W - 170, 40), 1)
R.text_a(img, (W - 24, H - 30), "Illustration · not actual likeness", R.F("inter", 22), (220, 210, 190), 0.9, "rm")
img.convert("RGB").resize((1280, 720), Image.LANCZOS).save(out, quality=90); print(out)
