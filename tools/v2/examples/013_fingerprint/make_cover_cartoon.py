"""Story cover for reel 013 with cartoon characters (illustrations, not likenesses) of two 1890s Bengal sub-inspectors."""
import sys, math
out = sys.argv[1]; sys.argv = ["x", "/home/claude/work/013t/spec.json"]
sys.path.insert(0, "/home/claude/unknown-uncovered/tools/v2")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import uu_render as R, uu_story as S
W, H = 1080, 1920; CY, AMB = (110, 240, 232), (255, 196, 96)
INK = (22, 18, 16, 255); SKIN = (182, 124, 84, 255); SKIN_D = (150, 98, 64, 255); KHAKI = (196, 168, 110, 255); KHAKI_D = (160, 132, 82, 255)
RED = (178, 38, 44, 255); RED_D = (130, 24, 30, 255); BELT = (110, 70, 32, 255); HAIR = (30, 24, 22, 255)
# ---------- background (same world as the video)
y = np.linspace(0, 1, H)[:, None, None]
bg = (np.array([4, 10, 14]) * (1 - y) + np.array([10, 30, 36]) * y)
img = Image.fromarray(np.broadcast_to(bg, (H, W, 3)).astype(np.uint8)).convert("RGBA")
g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse([90, 330, 990, 1230], fill=(30, 170, 175, 170)); img.alpha_composite(g.filter(ImageFilter.GaussianBlur(150)))
fp = S.fp_img(820, 1040, 7, CY, 0.5); img.alpha_composite(fp.filter(ImageFilter.GaussianBlur(6)), (130, 300)); img.alpha_composite(fp, (130, 300))
d = ImageDraw.Draw(img)
for side in (0, 1):
    for r in range(9):
        for c in range(3):
            x0 = (c * 92 + 8) if side == 0 else (W - (c + 1) * 92)
            y0 = 900 + r * 92
            d.rectangle([x0, y0, x0 + 84, y0 + 84], fill=(16, 34, 40, 235), outline=(60, 120, 125, 255), width=2)
            d.rectangle([x0 + 30, y0 + 36, x0 + 54, y0 + 44], fill=AMB + (200,))
            d.text((x0 + 42, y0 + 18), f"{(r * 3 + c) % 32 + 1}/{(r + 5 * c) % 32 + 1}", font=R.F("mono", 14), fill=(120, 170, 170, 200), anchor="mm")
fl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(fl).ellipse([60, 1660, 1020, 1880], fill=(60, 200, 200, 110)); img.alpha_composite(fl.filter(ImageFilter.GaussianBlur(40)))

# ---------- cartoon characters, drawn at 2x for smooth edges
K = 2; C = Image.new("RGBA", (W * K, H * K), (0, 0, 0, 0)); cd = ImageDraw.Draw(C)
OW = 7 * K
def E(box, fill, w=OW): cd.ellipse([v * K for v in box], fill=fill, outline=INK, width=w)
def P(pts, fill, w=OW): cd.polygon([(x * K, y * K) for x, y in pts], fill=fill, outline=INK, width=w)
def RR(box, r, fill, w=OW): cd.rounded_rectangle([v * K for v in box], r * K, fill=fill, outline=INK, width=w)
def L(pts, fill=INK, w=OW): cd.line([(x * K, y * K) for x, y in pts], fill=fill, width=w, joint="curve")
def A(box, a0, a1, fill=INK, w=OW): cd.arc([v * K for v in box], a0, a1, fill=fill, width=w)

def cop(cx, base, u, look="card", specs=False, moustache="thick"):
    hy = base - 76 * u                                                      # head centre
    # legs + shoes
    for sx in (-1, 1):
        RR([cx + sx * 1.5 * u - (9 * u if sx < 0 else 0), base - 30 * u, cx + sx * 1.5 * u + (9 * u if sx > 0 else 0), base - 4 * u], 3 * u, KHAKI_D)
        E([cx + sx * 6 * u - 7 * u, base - 7 * u, cx + sx * 6 * u + 7 * u + sx * 3 * u, base + 1 * u], INK)
    # tunic
    P([(cx - 15 * u, base - 60 * u), (cx + 15 * u, base - 60 * u), (cx + 17 * u, base - 27 * u), (cx - 17 * u, base - 27 * u)], KHAKI)
    RR([cx - 15.5 * u, base - 44 * u, cx + 15.5 * u, base - 40 * u], 1 * u, BELT, OW // 2)
    RR([cx - 3 * u, base - 45 * u, cx + 3 * u, base - 39 * u], 1 * u, AMB + (255,), OW // 2)
    for k in range(4): E([cx - 1.3 * u, base - (57 - k * 4) * u, cx + 1.3 * u, base - (54.4 - k * 4) * u], AMB + (255,), OW // 3)
    E([cx - 6 * u, base - 63 * u, cx + 6 * u, base - 57 * u], KHAKI)               # collar
    # arms
    if look == "card":
        P([(cx - 15 * u, base - 59 * u), (cx - 21 * u, base - 55 * u), (cx - 19 * u, base - 33 * u), (cx - 14 * u, base - 34 * u)], KHAKI)   # hanging arm
        E([cx - 21 * u, base - 36 * u, cx - 13 * u, base - 28 * u], SKIN)
        P([(cx + 13 * u, base - 59 * u), (cx + 19 * u, base - 55 * u), (cx + 21 * u, base - 46 * u), (cx + 10 * u, base - 44 * u)], KHAKI)    # raised arm to card
    else:
        P([(cx - 15 * u, base - 59 * u), (cx - 21 * u, base - 55 * u), (cx - 19 * u, base - 33 * u), (cx - 14 * u, base - 34 * u)], KHAKI)
        E([cx - 21 * u, base - 36 * u, cx - 13 * u, base - 28 * u], SKIN)
        pass   # the magnifier arm is drawn after the head (see below)
    # head + ears
    E([cx - 13.5 * u, hy - 2.5 * u, cx - 9 * u, hy + 4.5 * u], SKIN); E([cx + 9 * u, hy - 2.5 * u, cx + 13.5 * u, hy + 4.5 * u], SKIN)
    E([cx - 11 * u, hy - 11 * u, cx + 11 * u, hy + 12 * u], SKIN)
    # pagri (rounded wrapped turban with folds)
    E([cx - 13 * u, hy - 21 * u, cx + 13 * u, hy - 2 * u], RED)
    for k in range(3): A([cx - 12 * u, hy - (19 - k * 4.5) * u, cx + 12 * u, hy - (7 - k * 4.5) * u], 200, 340, RED_D, OW)
    E([cx - 3 * u, hy - 9 * u, cx + 3 * u, hy - 3 * u], AMB + (255,), OW // 2)    # badge
    # face
    for sx in (-1, 1):
        E([cx + sx * 4.2 * u - 2.4 * u, hy - 0.5 * u, cx + sx * 4.2 * u + 2.4 * u, hy + 4.5 * u], (255, 255, 255, 255), OW // 2)
        E([cx + sx * 4.2 * u - 1.1 * u + (0.6 * u if look == "card" else -0.6 * u), hy + 1.2 * u, cx + sx * 4.2 * u + 1.1 * u + (0.6 * u if look == "card" else -0.6 * u), hy + 3.6 * u], INK, 1)
        L([(cx + sx * 6.5 * u, hy - 2.5 * u), (cx + sx * 2 * u, hy - 1.8 * u)], HAIR, OW)
        if specs: cd.ellipse([(cx + sx * 4.2 * u - 3.4 * u) * K, (hy - 1.2 * u) * K, (cx + sx * 4.2 * u + 3.4 * u) * K, (hy + 5.6 * u) * K], outline=INK, width=OW // 2)
    if specs: L([(cx - 0.8 * u, hy + 1.8 * u), (cx + 0.8 * u, hy + 1.8 * u)], INK, OW // 2)
    A([cx - 1.6 * u, hy + 3 * u, cx + 1.6 * u, hy + 7.4 * u], 300, 80, SKIN_D, OW // 2)    # nose
    if moustache == "thick":
        P([(cx - 6.5 * u, hy + 8.4 * u), (cx - 1 * u, hy + 6.8 * u), (cx, hy + 7.6 * u), (cx + 1 * u, hy + 6.8 * u), (cx + 6.5 * u, hy + 8.4 * u), (cx + 4 * u, hy + 9.6 * u), (cx, hy + 8.8 * u), (cx - 4 * u, hy + 9.6 * u)], HAIR, OW // 2)
    else:
        P([(cx - 4.5 * u, hy + 8.2 * u), (cx, hy + 7.2 * u), (cx + 4.5 * u, hy + 8.2 * u), (cx, hy + 8.8 * u)], HAIR, OW // 3)
    A([cx - 3.5 * u, hy + 7.5 * u, cx + 3.5 * u, hy + 11.5 * u], 20, 160, INK, OW // 2)    # smile
    return hy

u1, u2 = 10.2, 10.6
hyA = cop(330, 1830, u1, "card", specs=True, moustache="thin")
hyB = cop(752, 1840, u2, "glass", specs=False, moustache="thick")
# prop A: ten-print card held up
cx_, cy_ = 330 + 19 * u1, 1830 - 50 * u1
card = Image.new("RGBA", (200 * K, 140 * K), (240, 234, 214, 255)); kd = ImageDraw.Draw(card); kd.rectangle([0, 0, card.width - 1, card.height - 1], outline=INK, width=OW)
for i in range(5):
    card.alpha_composite(S.fp_img(30 * K, 40 * K, 40 + i, (40, 40, 40), 1.0), ((10 + i * 37) * K, 18 * K))
    card.alpha_composite(S.fp_img(30 * K, 40 * K, 50 + i, (40, 40, 40), 1.0), ((10 + i * 37) * K, 78 * K))
card = card.rotate(10, expand=True, resample=Image.BICUBIC)
C.alpha_composite(card, (int((cx_ - 40) * K), int((cy_ - 120) * K)))
cd = ImageDraw.Draw(C)
E([cx_ - 7, cy_ - 6, cx_ + 7, cy_ + 8], SKIN)                                             # hand over the card edge
# prop B: magnifying glass at the eye, eye magnified (cartoon gag)
ex, ey = 752 + 4.2 * u2, hyB + 2 * u2
cxB, bB = 752, 1840
sh_ = (cxB + 15 * u2, bB - 57 * u2); el = (cxB + 23 * u2, bB - 44 * u2); hd = (ex + 62, ey + 118)
L([sh_, el, hd], INK, int(7.4 * u2 * K)); L([sh_, el, hd], KHAKI, int(5.6 * u2 * K))     # bent arm: shoulder -> elbow -> hand
L([(hd[0] - 6, hd[1] - 8), (ex + 26, ey + 46)], INK, 22 * K); L([(hd[0] - 6, hd[1] - 8), (ex + 26, ey + 46)], (160, 108, 44, 255), 14 * K)   # handle
E([hd[0] - 18, hd[1] - 16, hd[0] + 18, hd[1] + 18], SKIN)                               # hand
cd.ellipse([(ex - 58) * K, (ey - 58) * K, (ex + 58) * K, (ey + 58) * K], fill=(200, 255, 250, 110), outline=AMB + (255,), width=12 * K)
E([ex - 30, ey - 26, ex + 30, ey + 26], (255, 255, 255, 255), OW // 2); E([ex - 15, ey - 12, ex + 9, ey + 14], INK, 1)
E([ex - 9, ey - 8, ex - 3, ey - 2], (255, 255, 255, 255), 1)
figs = C.resize((W, H), Image.LANCZOS)
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sh.putalpha(figs.getchannel("A").filter(ImageFilter.GaussianBlur(26)).point(lambda v: v // 2))
rim = Image.new("RGBA", (W, H), CY + (0,)); rim.putalpha(figs.getchannel("A").filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(12)).point(lambda v: int(v * 0.8)))
img.alpha_composite(sh, (12, 18)); img.alpha_composite(rim); img.alpha_composite(figs)
# ---------- title block
R.text_a(img, (W / 2, 250), "1897  ·  CALCUTTA", R.F("mono", 34), CY, 1, "mm", shadow=6)
R.text_a(img, (W / 2, 360), "फ़िंगरप्रिंट के", R.F("hindi", 120), R.WHITE, 1, "mm", stroke=8, shadow=14)
R.text_a(img, (W / 2, 520), "भूले हुए हीरो", R.F("hindi", 150), AMB, 1, "mm", stroke=9, shadow=16)
f = R.F("disp", 40, "Black"); txt = "AZIZUL HAQUE  &  HEM CHANDRA BOSE"
tw = ImageDraw.Draw(img).textlength(txt, font=f); R.rect_a(img, (W / 2 - tw / 2 - 30, 640, W / 2 + tw / 2 + 30, 712), (180, 30, 40), 0.95, 12)
R.text_a(img, (W / 2, 676), txt, f, R.WHITE, 1, "mm")
tag = "THE INDIANS BEHIND THE WORLD'S FIRST FINGERPRINT BUREAU"
R.text_a(img, (W / 2, 760), tag, R.fit_font("mono", 26, tag, W - 80), R.WHITE, 1, "mm", shadow=8)
R.text_a(img, (W - 30, 1890), "Illustration · not actual likeness", R.F("inter", 20), (170, 190, 190), 1, "rm")
R.paste_a(img, R.LOGO.resize((110, 110), Image.LANCZOS), (W - 150, 60), 1)
yy, xx = np.mgrid[0:H, 0:W]; v = np.clip(1 - (((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.7)) ** 2) * 0.55, 0.4, 1)
Image.fromarray((np.array(img.convert("RGB")).astype(np.float32) * v[..., None]).astype(np.uint8)).save(out, quality=90)
print(out)
