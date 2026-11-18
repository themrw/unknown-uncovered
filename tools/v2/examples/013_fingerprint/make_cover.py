"""Story-cover thumbnail for reel 013: two 1890s Bengal policemen (illustrated silhouettes, no real likeness)."""
import sys, math
out = sys.argv[1]; sys.argv = ["x", "/home/claude/work/013t/spec.json"]
sys.path.insert(0, "/home/claude/unknown-uncovered/tools/v2")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import uu_render as R, uu_story as S
W, H = 1080, 1920
CY, AMB = (110, 240, 232), (255, 196, 96)
# ---- background: teal gradient + giant fingerprint 'moon' + wall of drawers
y = np.linspace(0, 1, H)[:, None, None]
bg = (np.array([4, 10, 14]) * (1 - y) + np.array([10, 30, 36]) * y)
img = Image.fromarray(np.broadcast_to(bg, (H, W, 3)).astype(np.uint8)).convert("RGBA")
g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse([90, 330, 990, 1230], fill=(30, 170, 175, 170)); img.alpha_composite(g.filter(ImageFilter.GaussianBlur(150)))
fp = S.fp_img(820, 1040, 7, CY, 0.55); img.alpha_composite(fp.filter(ImageFilter.GaussianBlur(6)), (130, 300)); img.alpha_composite(fp, (130, 300))
wall = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(wall)
for side in (0, 1):                                     # two drawer walls receding left and right
    for r in range(9):
        for c in range(3):
            x0 = (c * 92 + 8) if side == 0 else (W - (c + 1) * 92 - 8 + 8)
            y0 = 900 + r * 92 - (2 - c) * 0
            col = (16, 34, 40, 235); d.rectangle([x0, y0, x0 + 84, y0 + 84], fill=col, outline=(60, 120, 125, 255), width=2)
            d.rectangle([x0 + 30, y0 + 36, x0 + 54, y0 + 44], fill=AMB + (200,))
            d.text((x0 + 42, y0 + 18), f"{(r * 3 + c) % 32 + 1}/{(r + 5 * c) % 32 + 1}", font=R.F("mono", 14), fill=(120, 170, 170, 200), anchor="mm")
img.alpha_composite(wall)
fl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(fl).ellipse([60, 1640, 1020, 1860], fill=(60, 200, 200, 120)); img.alpha_composite(fl.filter(ImageFilter.GaussianBlur(40)))

# ---- figures
def figure(cx, base, h, flip=1, prop="card"):
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
    top = base - h; u = h / 100
    hx, hy = cx, top + 15 * u                                         # head centre
    d.ellipse([hx - 5.5 * u, hy - 6.5 * u, hx + 5.5 * u, hy + 6.5 * u], fill=255)               # head
    d.ellipse([hx - 8.5 * u, hy - 14 * u, hx + 8.5 * u, hy - 1.5 * u], fill=255)                 # pagri: a full, rounded wrapped turban
    d.ellipse([hx - 7 * u, hy - 16 * u, hx + 7 * u, hy - 7 * u], fill=255)
    d.polygon([(hx - flip * 6 * u, hy - 4 * u), (hx - flip * 10 * u, hy + 6 * u), (hx - flip * 7 * u, hy + 7 * u), (hx - flip * 4 * u, hy - 2 * u)], fill=255)   # cloth tail at the back
    d.rectangle([hx - 2.6 * u, hy + 5 * u, hx + 2.6 * u, hy + 9.5 * u], fill=255)              # neck
    sh = hy + 9 * u
    d.polygon([(cx - 13 * u, sh + 2 * u), (cx + 13 * u, sh + 2 * u), (cx + 10.5 * u, sh + 34 * u), (cx + 12.5 * u, sh + 50 * u),
               (cx - 12.5 * u, sh + 50 * u), (cx - 10.5 * u, sh + 34 * u)], fill=255)            # tunic to the knee
    d.chord([cx - 14 * u, sh - 1 * u, cx + 14 * u, sh + 9 * u], 180, 360, fill=255)              # sloped shoulders
    for sx in (-1, 1):                                                 # trousers + shoes
        d.polygon([(cx + sx * 1.5 * u, sh + 49 * u), (cx + sx * 8.5 * u, sh + 49 * u), (cx + sx * 7.5 * u, base - 2 * u), (cx + sx * 2.5 * u, base - 2 * u)], fill=255)
        xa, xb = sorted([cx + sx * 2 * u, cx + sx * 11 * u]); d.ellipse([xa, base - 4 * u, xb, base + 1 * u], fill=255)
    # arms: the 'outside' arm hangs, the 'inside' arm is raised to the chest holding the prop
    out = -flip; d.polygon([(cx + out * 12 * u, sh + 3 * u), (cx + out * 16.5 * u, sh + 6 * u), (cx + out * 15.5 * u, sh + 42 * u), (cx + out * 11.5 * u, sh + 42 * u)], fill=255)
    hand = (cx + flip * 9 * u, sh + 24 * u)
    d.polygon([(cx + flip * 11 * u, sh + 3 * u), (cx + flip * 15.5 * u, sh + 7 * u), (cx + flip * 14 * u, sh + 26 * u), hand, (hand[0] - flip * 2 * u, hand[1] - 5 * u), (cx + flip * 10 * u, sh + 20 * u)], fill=255)
    return m, hand, u, sh, (hx, hy)

def paint(m, sh_y, u, cx, head):
    fill = Image.new("RGBA", (W, H), (8, 18, 22, 255)); body = Image.new("RGBA", (W, H), (0, 0, 0, 0)); body.paste(fill, (0, 0), m)
    d = ImageDraw.Draw(body)
    d.rectangle([cx - 12.5 * u, sh_y + 33 * u, cx + 12.5 * u, sh_y + 36 * u], fill=(120, 80, 30, 255))      # belt
    d.rectangle([cx - 2 * u, sh_y + 32.5 * u, cx + 2 * u, sh_y + 36.5 * u], fill=AMB + (255,))             # buckle
    for k in range(5): d.ellipse([cx - 0.8 * u, sh_y + (6 + k * 5.5) * u, cx + 0.8 * u, sh_y + (7.6 + k * 5.5) * u], fill=AMB + (255,))   # buttons
    hx, hy = head
    for k in range(3):                                                 # turban folds
        d.arc([hx - 8 * u, hy - (13 - k * 3.2) * u, hx + 8 * u, hy - (5 - k * 3.2) * u], 200, 340, fill=(40, 90, 96, 255), width=max(2, int(u * 0.5)))
    d.line([cx, sh_y + 2 * u, cx, sh_y + 33 * u], fill=(20, 40, 46, 255), width=max(2, int(u * 0.3)))
    edge = ImageChops.subtract(m, m.filter(ImageFilter.MinFilter(9)))
    rim = Image.new("RGBA", (W, H), CY + (0,)); rim.putalpha(edge)
    glow = Image.new("RGBA", (W, H), CY + (0,)); glow.putalpha(edge.filter(ImageFilter.GaussianBlur(14)))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); shadow.putalpha(m.filter(ImageFilter.GaussianBlur(30)).point(lambda v: v // 2))
    return [shadow, glow, glow, body, rim]

layers = []
mA, handA, uA, shA, hA = figure(360, 1820, 840, flip=1, prop="card")
mB, handB, uB, shB, hB = figure(730, 1830, 880, flip=-1, prop="glass")
for L in paint(mA, shA, uA, 360, hA) + paint(mB, shB, uB, 730, hB): img.alpha_composite(L)
d = ImageDraw.Draw(img)
# prop A: a ten-print card glowing
cx_, cy_ = handA; card = Image.new("RGBA", (150, 104), (236, 230, 210, 255)); cd = ImageDraw.Draw(card)
for i in range(5): card.alpha_composite(S.fp_img(24, 32, 40 + i, (40, 40, 40), 1.0), (8 + i * 28, 16)); card.alpha_composite(S.fp_img(24, 32, 50 + i, (40, 40, 40), 1.0), (8 + i * 28, 60))
card = card.rotate(-12, expand=True, resample=Image.BICUBIC); gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).ellipse([cx_ - 60, cy_ - 140, cx_ + 160, cy_ + 40], fill=(255, 240, 200, 120))
img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(40))); img.alpha_composite(card, (int(cx_ - 20), int(cy_ - 130)))
# prop B: magnifying glass
bx, by = handB; lx, ly = bx - 70, by - 120
d.line([bx, by, lx + 30, ly + 34], fill=(150, 100, 40, 255), width=14)
d.ellipse([lx - 52, ly - 52, lx + 52, ly + 52], outline=AMB + (255,), width=10)
lens = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(lens).ellipse([lx - 46, ly - 46, lx + 46, ly + 46], fill=CY + (90,)); img.alpha_composite(lens)
img.alpha_composite(S.fp_img(70, 84, 7, (230, 255, 250), 0.9), (int(lx - 35), int(ly - 42)))
# ---- title block (story cover)
R.text_a(img, (W / 2, 250), "1897  ·  CALCUTTA", R.F("mono", 34), CY, 1, "mm", shadow=6)
R.text_a(img, (W / 2, 360), "फ़िंगरप्रिंट के", R.F("hindi", 120), R.WHITE, 1, "mm", stroke=8, shadow=14)
R.text_a(img, (W / 2, 520), "भूले हुए हीरो", R.F("hindi", 150), AMB, 1, "mm", stroke=9, shadow=16)
f = R.F("disp", 40, "Black"); txt = "AZIZUL HAQUE  &  HEM CHANDRA BOSE"
tw = ImageDraw.Draw(img).textlength(txt, font=f); R.rect_a(img, (W / 2 - tw / 2 - 30, 640, W / 2 + tw / 2 + 30, 712), (180, 30, 40), 0.95, 12)
R.text_a(img, (W / 2, 676), txt, f, R.WHITE, 1, "mm")
R.text_a(img, (W / 2, 760), "THE INDIANS BEHIND THE WORLD'S FIRST FINGERPRINT BUREAU", R.fit_font("mono", 26, "THE INDIANS BEHIND THE WORLD'S FIRST FINGERPRINT BUREAU", W - 80), R.WHITE, 1, "mm", shadow=8)
R.paste_a(img, R.LOGO.resize((110, 110), Image.LANCZOS), (W - 150, 60), 1)
v = np.ones((H, W), np.float32); yy, xx = np.mgrid[0:H, 0:W]; v = np.clip(1 - (((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.7)) ** 2) * 0.55, 0.4, 1)
arr = np.array(img.convert("RGB")).astype(np.float32) * v[..., None]
Image.fromarray(arr.astype(np.uint8)).save(out, quality=90)
print(out)
