import sys, math
sys.argv = ["x", "/home/claude/work/015/spec.json"]
sys.path.insert(0, "/home/claude/unknown-uncovered/tools/v2")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import uu_story as S
T = S.T; W, H = 1080, 1920
bg = Image.fromarray(np.tile(np.array([10, 8, 4], np.uint8), (H, W, 1))).convert("RGBA")
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
gd.ellipse([-100, 520, 760, 1400], fill=(255, 190, 60, 110)); gd.ellipse([520, 640, 1180, 1300], fill=(60, 200, 130, 70))
bg.alpha_composite(glow.filter(ImageFilter.GaussianBlur(150)))
# phone with QR + success tick
ph = Image.new("RGBA", (420, 640), (0, 0, 0, 0)); d = ImageDraw.Draw(ph)
d.rounded_rectangle([0, 0, 419, 639], 60, fill=(18, 18, 22, 255), outline=T["accent"] + (255,), width=6)
d.rounded_rectangle([22, 70, 397, 600], 30, fill=(250, 250, 246, 255))
d.rounded_rectangle([160, 26, 260, 42], 8, fill=(40, 40, 46, 255))
ph.alpha_composite(S.qr_img(25, 300, 3), (60, 120))
d.ellipse([260, 380, 390, 510], fill=(40, 186, 110, 255)); S.tick_mark(d, 325, 445, 80, (255, 255, 255, 255), 12)
ph = ph.rotate(8, expand=True, resample=Image.BICUBIC)
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sh.alpha_composite(Image.new("RGBA", ph.size, (0, 0, 0, 0)), (0, 0))
shadow = Image.new("RGBA", ph.size, (0, 0, 0, 0)); shadow.putalpha(ph.getchannel("A").point(lambda v: int(v * 0.6)))
bg.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(24)), (80, 680)); bg.alpha_composite(ph, (55, 640))
# three keys on the right
for i, (lab, col) in enumerate([("JIO", T["accent2"]), ("PAYTM", T["accent2"]), ("?", T["alert"])]):
    y = 790 + i * 130; x = 560
    box = Image.new("RGBA", (440, 120), (0, 0, 0, 0)); bd = ImageDraw.Draw(box)
    bd.rounded_rectangle([0, 0, 439, 119], 26, fill=(30, 26, 16, 235) if lab != "?" else (70, 16, 16, 240), outline=col + (255,), width=5)
    if lab != "?":
        box.alpha_composite(S.key_icon(170, col + (255,)), (20, 18))
        bd.text((320, 62), lab, font=S.fit_font("anton", 70, lab, 200), fill=(245, 245, 240, 255), anchor="mm")
    else:
        bd.text((220, 60), "?  ?  ?", font=S.F("anton", 86), fill=col + (255,), anchor="mm")
    bg.alpha_composite(box, (x, y))
bg.convert("RGB").save("/home/claude/work/015/thumb_bg.jpg", quality=95)
print("ok")
