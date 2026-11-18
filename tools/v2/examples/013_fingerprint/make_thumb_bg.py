import sys
sys.argv = ["x", "/home/claude/work/013t/spec.json"]
sys.path.insert(0, "/home/claude/unknown-uncovered/tools/v2")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import uu_story as S
W, H = 1080, 1920
yy = np.linspace(0, 1, H)[:, None]; base = np.array([5, 12, 16])[None, None, :] * (1 + 0 * yy[..., None])
bg = Image.fromarray(np.tile(np.array([6, 13, 18], np.uint8), (H, W, 1))).convert("RGBA")
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(glow).ellipse([60, 420, 1020, 1500], fill=(20, 140, 150, 140))
bg.alpha_composite(glow.filter(ImageFilter.GaussianBlur(140)))
fp = S.fp_img(760, 980, 7, (110, 240, 232), 1.0)
fpg = fp.filter(ImageFilter.GaussianBlur(10)); bg.alpha_composite(fpg, (160, 470)); bg.alpha_composite(fp, (160, 470))
red = S.fp_img(760, 980, 7, (230, 50, 60), 0.9).crop((0, 600, 760, 980)); bg.alpha_composite(red, (160, 1070))   # lower part 'evidence red'
line = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(line).rectangle([90, 1066, 990, 1074], fill=(150, 255, 245, 255))
bg.alpha_composite(line.filter(ImageFilter.GaussianBlur(8))); bg.alpha_composite(line)
d = ImageDraw.Draw(bg)
for (mx, my) in S.MINU: x, y = 160 + mx * 760, 470 + my * 980; d.ellipse([x - 26, y - 26, x + 26, y + 26], outline=(255, 196, 96, 255), width=5)
bg.convert("RGB").save("thumb_bg.jpg", quality=95)
