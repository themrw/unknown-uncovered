#!/usr/bin/env python3
"""16:9 thumbnail (1280x720 JPG) for a long-form spec.

usage: uu_thumb_long.py spec.json out.jpg
spec["thumb"] = {"hook": ["Hindi line 1", "Hindi line 2"], "number": "12,187", "number_label": "NUCLEAR WARHEADS",
                 "sticker": "भारत कहाँ?", "img": "media/.../photo.jpg", "highlight": ["CN", "IN"], "view": [30, 85],
                 "mystery": ["CN", "IN", "PK"]}
Drawn at 1920x1080 and downscaled. Big text stays left; photo + globe right.
"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter
import uu_long as L
R = L.R
TH = R.SPEC["thumb"]; W, H, T = R.W, R.H, R.T
out = sys.argv[2]

img = R.BG.crop((60, 60, 60 + W, 60 + H))
if TH.get("img"):
    src = L.load(TH["img"])
    ph = src.crop(((src.width - W) // 2, (src.height - H) // 2, (src.width - W) // 2 + W, (src.height - H) // 2 + H)).convert("RGBA")
    img.alpha_composite(ph)
    img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 90)))
L.gradient(img, "left", 0.97, 0.7)
lat, lon = TH.get("view", [30, 85])
g = R.GLOBE.render(lat, lon, highlight=TH.get("highlight"), hl_alpha=1, dim_others=0.3, pulse=1, hide=True)
g = g.resize((int(g.width * 1.35),) * 2, Image.LANCZOS)
halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(halo).ellipse([W - 760, H / 2 - 520, W + 280, H / 2 + 520], fill=T["alert"] + (90,))
img.alpha_composite(halo.filter(ImageFilter.GaussianBlur(80)))
R.paste_a(img, g, (W - g.width * 0.72, H / 2 - g.height / 2 + 40), 0.95)
for i, line in enumerate(TH.get("hook", [])):
    f = R.fit_font("hindi", 170, line, 1180)
    R.text_a(img, (70, 70 + i * 190), line, f, R.WHITE if i == 0 else T["accent"], 1, stroke=12, shadow=16)
if TH.get("number"):
    R.text_a(img, (70, 520), TH["number"], R.F("anton", 260), T["alert"], 1, stroke=8, shadow=16)
    R.text_a(img, (80, 820), TH.get("number_label", ""), R.F("disp", 64, "Black"), R.WHITE, 1, stroke=5, shadow=10)
if TH.get("sticker"):
    f = R.F("hindi", 84); tw = ImageDraw.Draw(img).textlength(TH["sticker"], font=f)
    st = Image.new("RGBA", (int(tw) + 90, 150), (0, 0, 0, 0)); d = ImageDraw.Draw(st)
    d.rounded_rectangle((4, 4, st.width - 4, st.height - 4), 30, fill=T["alert"] + (255,), outline=(255, 255, 255, 255), width=6)
    d.text((st.width / 2, st.height / 2 + 4), TH["sticker"], font=f, fill=(255, 255, 255), anchor="mm")
    st = st.rotate(-6, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(st, (W - st.width - 60, H - st.height - 70))
codes = TH.get("mystery", [])
for i, c in enumerate(codes):
    x = 80 + i * 150; y = 930
    R.rect_a(img, (x, y, x + 130, y + 100), (12, 12, 12), 0.92, 14, T["alert"], 3)
    fl = R.silhouette(R.flag(c, 104), (40, 40, 40))
    R.paste_a(img, fl, (x + 65 - fl.width / 2, y + 50 - fl.height / 2), 1)
    R.text_a(img, (x + 65, y + 50), "?", R.F("anton", 70), R.WHITE, 1, "mm", stroke=3)
R.paste_a(img, R.LOGO.resize((110, 110), Image.LANCZOS), (W - 150, 40), 1)
img.convert("RGB").resize((1280, 720), Image.LANCZOS).save(out, "JPEG", quality=90, optimize=True)
print(out, os.path.getsize(out))
