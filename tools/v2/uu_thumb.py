#!/usr/bin/env python3
"""Themed 1080x1920 thumbnail for a v2 spec, using the renderer's theme, globe, flags and logo.

usage: uu_thumb.py spec.json [out.jpg]      (default <spec dir>/out/thumbnail.jpg)

spec["thumb"] = {
  "hook": ["Hindi line 1", "Hindi line 2"],    # big stroked Mukta ExtraBold, 2nd line in accent
  "number": "+270", "number_label": "WARHEADS IN 5 YEARS",
  "sticker": "भारत कहाँ?",                       # curiosity sticker
  "highlight": ["CN", "IN"], "view": [25, 80],  # glowing countries (red, unnamed) and globe centre
  "mystery": ["GB", "PK", "KP", "IN", "CN"]     # silhouette flags with "?" (no answers given away)
}
Key content stays inside the central 1080x1440 (y 240..1680) so the Instagram grid crop keeps it.
"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter
import uu_render as R   # reads sys.argv[1] (the spec) on import

TH = R.SPEC["thumb"]
W, H, T = R.W, R.H, R.T
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(R.OUT, "thumbnail.jpg")
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)

img = R.BG.crop((60, 60, 60 + W, 60 + H))
R.particles(img, 2.0)

# globe: highlighted countries glow in the alert colour (unnamed), slightly enlarged
lat, lon = TH.get("view", [25, 75])
g = R.GLOBE.render(lat, lon, highlight=TH.get("highlight"), hl_alpha=1, dim_others=0.35, pulse=1, hide=True)
s = 1.35; g = g.resize((int(g.width * s),) * 2, Image.LANCZOS)
gx, gy = W / 2 - g.width / 2, 1040 - g.height / 2
halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(halo).ellipse([W / 2 - 520, 1040 - 520, W / 2 + 520, 1040 + 520], fill=T["alert"] + (70,))
img.alpha_composite(halo.filter(ImageFilter.GaussianBlur(90)))
R.paste_a(img, g, (gx, gy), 1)
m = R.motif_img(150); R.paste_a(img, m.rotate(-20, resample=Image.BICUBIC, expand=False), (W - 260, 610), 0.18)

# scan rings around the first highlighted country
if TH.get("highlight") and TH["highlight"][0] in R.CENTROID:
    (px, py), vis = R.GLOBE.point(*R.CENTROID[TH["highlight"][0]], lat, lon)
    if vis > 0:
        cx, cy = gx + px * s, gy + py * s; d = ImageDraw.Draw(img)
        for rr, a in ((40, 230), (80, 150), (125, 80)):
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=T["accent"] + (a,), width=5)

# top: logo + hook
R.paste_a(img, R.LOGO.resize((120, 120), Image.LANCZOS), (W - 70 - 120, 250), 1)
hook = TH.get("hook", [])
for i, line in enumerate(hook):
    f = R.F("hindi", 150 if len(line) <= 12 else 124)
    R.text_a(img, (64, 250 + i * 165), line, f, R.WHITE if i == 0 else T["accent"], 1, stroke=10, shadow=14)

# sticker
if TH.get("sticker"):
    f = R.F("hindi", 76); tw = ImageDraw.Draw(img).textlength(TH["sticker"], font=f)
    st = Image.new("RGBA", (int(tw) + 80, 130), (0, 0, 0, 0)); d = ImageDraw.Draw(st)
    d.rounded_rectangle((4, 4, st.width - 4, st.height - 4), 26, fill=T["alert"] + (255,), outline=(255, 255, 255, 255), width=5)
    d.text((st.width / 2, st.height / 2 + 4), TH["sticker"], font=f, fill=(255, 255, 255), anchor="mm")
    st = st.rotate(7, resample=Image.BICUBIC, expand=True)
    sh = Image.new("RGBA", st.size, (0, 0, 0, 0)); sh.putalpha(st.getchannel("A").point(lambda v: v // 2))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), (W - st.width - 40, 640))
    img.alpha_composite(st, (W - st.width - 50, 625))

# big number + label
if TH.get("number"):
    R.text_a(img, (64, 1140), TH["number"], R.F("anton", 300), T["accent"], 1, stroke=8, shadow=16)
    R.text_a(img, (74, 1505), TH.get("number_label", ""), R.F("disp", 56, "Black"), R.WHITE, 1, stroke=4, shadow=8)

# mystery flags row
codes = TH.get("mystery", [])
if codes:
    n = len(codes); cw = 160; gap = (W - 128 - n * cw) / max(1, n - 1)
    for i, c in enumerate(codes):
        x = 64 + i * (cw + gap); y = 1584
        R.rect_a(img, (x, y, x + cw, y + 104), (12, 14, 12), 0.92, 16, T["alert"] if i == n - 1 else T["land_edge"], 3)
        fl = R.silhouette(R.flag(c, 120), (40, 44, 40))
        R.paste_a(img, fl, (x + (cw - fl.width) / 2, y + (104 - fl.height) / 2), 1)
        R.text_a(img, (x + cw / 2, y + 52), "?", R.F("anton", 76), T["alert"] if i == n - 1 else R.WHITE, 1, "mm", stroke=3)

img.convert("RGB").save(out, "JPEG", quality=88, optimize=True)
print(out, os.path.getsize(out))
