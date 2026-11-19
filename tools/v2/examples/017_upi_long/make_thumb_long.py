"""16:9 thumbnail for long video 017: Raju's stall (fictional cartoon), soundbox rings, phone at the Eiffel Tower, proud hook."""
import sys
out = sys.argv[1]; sys.argv = ["x", "/home/claude/work/017/spec.json"]
sys.path.insert(0, "/home/claude/unknown-uncovered/tools/v2")
from PIL import Image, ImageDraw, ImageFilter
import uu_long as L, uu_story as S, uu_cartoon
R = L.R; W, H, T = R.W, R.H, R.T
img = R.BG.crop((60, 60, 60 + W, 60 + H))
g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
gd.ellipse([980, 60, 2000, 1160], fill=(255, 170, 50, 170)); gd.ellipse([1300, 300, 1900, 900], fill=(255, 230, 150, 90))
img.alpha_composite(g.filter(ImageFilter.GaussianBlur(130)))
d = ImageDraw.Draw(img); cx, ct = 1380, 1060 - 46 * 4.6
for j in range(4):
    r = 120 + j * 90; d.ellipse([cx - 32 * 4.6 - r, ct - 9 * 4.6 - r, cx - 32 * 4.6 + r, ct - 9 * 4.6 + r], outline=T["accent2"] + (200 - j * 45,), width=7)
img.alpha_composite(uu_cartoon.stall_layer(W, H, cx, 1060, 4.6, ("qr", "soundbox"), S.qr_img))
R.text_a(img, (cx, ct + 22 * 4.6), "राजू टी स्टॉल", R.F("hindi", int(13 * 4.6)), (120, 60, 20), 1, "mm")
ph = Image.new("RGBA", (380, 640), (0, 0, 0, 0)); pd = ImageDraw.Draw(ph)
pd.rounded_rectangle([0, 0, 379, 639], 40, fill=(16, 16, 20, 255), outline=T["accent"] + (255,), width=6)
ph.alpha_composite(uu_cartoon.eiffel_card(330, 560, S.qr_img), (25, 50))
ph = ph.rotate(-8, expand=True, resample=Image.BICUBIC)
sh = Image.new("RGBA", ph.size, (0, 0, 0, 0)); sh.putalpha(ph.getchannel("A").point(lambda v: int(v * 0.6)))
img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20)), (1560, 120)); img.alpha_composite(ph, (1540, 90))
L.gradient(img, "left", 0.9, 0.5)
hook = [("10 साल में", (245, 245, 240)), ("दुनिया में नंबर 1!", T["accent"])]
for i, (s, col) in enumerate(hook):
    f = R.fit_font("hindi", 150, s, 1000); R.text_a(img, (80, 120 + i * 190), s, f, col, 1, shadow=14)
R.text_a(img, (84, 560), "82 CRORE", R.F("anton", 190), (255, 255, 255), 1, shadow=14)
R.text_a(img, (92, 790), "UPI PAYMENTS EVERY DAY", R.F("disp", 56, "Black"), T["accent2"], 1, shadow=8)
st = "भारत का कमाल"; f = R.F("hindi", 64); w = ImageDraw.Draw(img).textlength(st, font=f)
lay = Image.new("RGBA", (int(w + 80), 120), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
ld.rounded_rectangle([0, 0, w + 79, 119], 26, fill=(220, 40, 40, 255), outline=(255, 255, 255, 255), width=5)
ld.text((w / 2 + 40, 58), st, font=f, fill=(255, 255, 255, 255), anchor="mm"); lay = lay.rotate(4, expand=True, resample=Image.BICUBIC)
img.alpha_composite(lay, (90, 880))
R.paste_a(img, R.LOGO if hasattr(R, "LOGO") else Image.new("RGBA", (1, 1)), (W - 170, 40), 1)
R.text_a(img, (W - 24, H - 30), "Illustration · fictional character", R.F("inter", 22), (200, 190, 170), 0.9, "rm")
img.convert("RGB").resize((1280, 720), Image.LANCZOS).save(out, quality=90); print(out)
