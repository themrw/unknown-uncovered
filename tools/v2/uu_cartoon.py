"""Cartoon characters for Unknown Uncovered: two 1890s Bengal sub-inspectors (illustrations, not likenesses).
officers_layer(W, H, xa, xb, base_a, base_b, ua, ub, card=True, glass=True) -> RGBA layer with both officers, props and a cyan rim glow."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

INK = (22, 18, 16, 255); SKIN = (182, 124, 84, 255); SKIN_D = (150, 98, 64, 255); KHAKI = (196, 168, 110, 255); KHAKI_D = (160, 132, 82, 255)
RED = (178, 38, 44, 255); RED_D = (130, 24, 30, 255); BELT = (110, 70, 32, 255); HAIR = (30, 24, 22, 255)
AMB = (255, 196, 96); CY = (110, 240, 232)

def officers_layer(W, H, xa, xb, ba, bb, ua, ub, card=True, glass=True, fp_img=None, rim=True):
    K = 2; C = Image.new("RGBA", (W * K, H * K), (0, 0, 0, 0)); cd = ImageDraw.Draw(C); OW = 7 * K
    def E(box, fill, w=OW): cd.ellipse([v * K for v in box], fill=fill, outline=INK, width=w)
    def P(pts, fill, w=OW): cd.polygon([(x * K, y * K) for x, y in pts], fill=fill, outline=INK, width=w)
    def RR(box, r, fill, w=OW): cd.rounded_rectangle([v * K for v in box], r * K, fill=fill, outline=INK, width=w)
    def L(pts, fill=INK, w=OW): cd.line([(x * K, y * K) for x, y in pts], fill=fill, width=w, joint="curve")
    def A(box, a0, a1, fill=INK, w=OW): cd.arc([v * K for v in box], a0, a1, fill=fill, width=w)
    def cop(cx, base, u, look, specs, moustache):
        hy = base - 76 * u
        for sx in (-1, 1):
            RR([cx + sx * 1.5 * u - (9 * u if sx < 0 else 0), base - 30 * u, cx + sx * 1.5 * u + (9 * u if sx > 0 else 0), base - 4 * u], 3 * u, KHAKI_D)
            E([cx + sx * 6 * u - 7 * u, base - 7 * u, cx + sx * 6 * u + 7 * u + sx * 3 * u, base + 1 * u], INK)
        P([(cx - 15 * u, base - 60 * u), (cx + 15 * u, base - 60 * u), (cx + 17 * u, base - 27 * u), (cx - 17 * u, base - 27 * u)], KHAKI)
        RR([cx - 15.5 * u, base - 44 * u, cx + 15.5 * u, base - 40 * u], 1 * u, BELT, OW // 2)
        RR([cx - 3 * u, base - 45 * u, cx + 3 * u, base - 39 * u], 1 * u, AMB + (255,), OW // 2)
        for k in range(4): E([cx - 1.3 * u, base - (57 - k * 4) * u, cx + 1.3 * u, base - (54.4 - k * 4) * u], AMB + (255,), OW // 3)
        E([cx - 6 * u, base - 63 * u, cx + 6 * u, base - 57 * u], KHAKI)
        P([(cx - 15 * u, base - 59 * u), (cx - 21 * u, base - 55 * u), (cx - 19 * u, base - 33 * u), (cx - 14 * u, base - 34 * u)], KHAKI)
        E([cx - 21 * u, base - 36 * u, cx - 13 * u, base - 28 * u], SKIN)
        if look == "card":
            P([(cx + 13 * u, base - 59 * u), (cx + 19 * u, base - 55 * u), (cx + 21 * u, base - 46 * u), (cx + 10 * u, base - 44 * u)], KHAKI)
        elif look == "rest":
            P([(cx + 15 * u, base - 59 * u), (cx + 21 * u, base - 55 * u), (cx + 19 * u, base - 33 * u), (cx + 14 * u, base - 34 * u)], KHAKI)
            E([cx + 13 * u, base - 36 * u, cx + 21 * u, base - 28 * u], SKIN)
        E([cx - 13.5 * u, hy - 2.5 * u, cx - 9 * u, hy + 4.5 * u], SKIN); E([cx + 9 * u, hy - 2.5 * u, cx + 13.5 * u, hy + 4.5 * u], SKIN)
        E([cx - 11 * u, hy - 11 * u, cx + 11 * u, hy + 12 * u], SKIN)
        E([cx - 13 * u, hy - 21 * u, cx + 13 * u, hy - 2 * u], RED)
        for k in range(3): A([cx - 12 * u, hy - (19 - k * 4.5) * u, cx + 12 * u, hy - (7 - k * 4.5) * u], 200, 340, RED_D, OW)
        E([cx - 3 * u, hy - 9 * u, cx + 3 * u, hy - 3 * u], AMB + (255,), OW // 2)
        for sx in (-1, 1):
            E([cx + sx * 4.2 * u - 2.4 * u, hy - 0.5 * u, cx + sx * 4.2 * u + 2.4 * u, hy + 4.5 * u], (255, 255, 255, 255), OW // 2)
            off = 0.6 * u if look == "card" else -0.6 * u
            E([cx + sx * 4.2 * u - 1.1 * u + off, hy + 1.2 * u, cx + sx * 4.2 * u + 1.1 * u + off, hy + 3.6 * u], INK, 1)
            L([(cx + sx * 6.5 * u, hy - 2.5 * u), (cx + sx * 2 * u, hy - 1.8 * u)], HAIR, OW)
            if specs: cd.ellipse([(cx + sx * 4.2 * u - 3.4 * u) * K, (hy - 1.2 * u) * K, (cx + sx * 4.2 * u + 3.4 * u) * K, (hy + 5.6 * u) * K], outline=INK, width=OW // 2)
        if specs: L([(cx - 0.8 * u, hy + 1.8 * u), (cx + 0.8 * u, hy + 1.8 * u)], INK, OW // 2)
        A([cx - 1.6 * u, hy + 3 * u, cx + 1.6 * u, hy + 7.4 * u], 300, 80, SKIN_D, OW // 2)
        if moustache == "thick":
            P([(cx - 6.5 * u, hy + 8.4 * u), (cx - 1 * u, hy + 6.8 * u), (cx, hy + 7.6 * u), (cx + 1 * u, hy + 6.8 * u), (cx + 6.5 * u, hy + 8.4 * u), (cx + 4 * u, hy + 9.6 * u), (cx, hy + 8.8 * u), (cx - 4 * u, hy + 9.6 * u)], HAIR, OW // 2)
        else:
            P([(cx - 4.5 * u, hy + 8.2 * u), (cx, hy + 7.2 * u), (cx + 4.5 * u, hy + 8.2 * u), (cx, hy + 8.8 * u)], HAIR, OW // 3)
        A([cx - 3.5 * u, hy + 7.5 * u, cx + 3.5 * u, hy + 11.5 * u], 20, 160, INK, OW // 2)
        return hy
    hyA = cop(xa, ba, ua, "card" if card else "rest", True, "thin")
    hyB = cop(xb, bb, ub, "glass" if glass else "rest", False, "thick")
    if card:
        cx_, cy_ = xa + 19 * ua, ba - 50 * ua; cw, ch = int(20 * ua), int(14 * ua)
        cardim = Image.new("RGBA", (cw * K, ch * K), (240, 234, 214, 255)); kd = ImageDraw.Draw(cardim); kd.rectangle([0, 0, cardim.width - 1, cardim.height - 1], outline=INK, width=OW)
        if fp_img:
            pw, ph = int(cw * K * 0.15), int(ch * K * 0.29)
            for i in range(5):
                cardim.alpha_composite(fp_img(pw, ph, 40 + i, (40, 40, 40), 1.0), (int(cw * K * (0.05 + i * 0.185)), int(ch * K * 0.12)))
                cardim.alpha_composite(fp_img(pw, ph, 50 + i, (40, 40, 40), 1.0), (int(cw * K * (0.05 + i * 0.185)), int(ch * K * 0.56)))
        cardim = cardim.rotate(10, expand=True, resample=Image.BICUBIC)
        C.alpha_composite(cardim, (int((cx_ - 4 * ua) * K), int((cy_ - 12 * ua) * K))); cd = ImageDraw.Draw(C)
        E([cx_ - 0.7 * ua, cy_ - 0.6 * ua, cx_ + 0.7 * ua, cy_ + 0.8 * ua], SKIN)
    if glass:
        ex, ey = xb + 4.2 * ub, hyB + 2 * ub
        sh_ = (xb + 15 * ub, bb - 57 * ub); el = (xb + 23 * ub, bb - 44 * ub); hd = (ex + 6.2 * ub, ey + 11.8 * ub)
        L([sh_, el, hd], INK, int(7.4 * ub * K)); L([sh_, el, hd], KHAKI, int(5.6 * ub * K))
        L([(hd[0] - 0.6 * ub, hd[1] - 0.8 * ub), (ex + 2.6 * ub, ey + 4.6 * ub)], INK, int(2.2 * ub * K)); L([(hd[0] - 0.6 * ub, hd[1] - 0.8 * ub), (ex + 2.6 * ub, ey + 4.6 * ub)], (160, 108, 44, 255), int(1.4 * ub * K))
        E([hd[0] - 1.8 * ub, hd[1] - 1.6 * ub, hd[0] + 1.8 * ub, hd[1] + 1.8 * ub], SKIN)
        r = 5.8 * ub
        cd.ellipse([(ex - r) * K, (ey - r) * K, (ex + r) * K, (ey + r) * K], fill=(200, 255, 250, 110), outline=AMB + (255,), width=int(1.2 * ub * K))
        E([ex - 3 * ub, ey - 2.6 * ub, ex + 3 * ub, ey + 2.6 * ub], (255, 255, 255, 255), OW // 2); E([ex - 1.5 * ub, ey - 1.2 * ub, ex + 0.9 * ub, ey + 1.4 * ub], INK, 1)
        E([ex - 0.9 * ub, ey - 0.8 * ub, ex - 0.3 * ub, ey - 0.2 * ub], (255, 255, 255, 255), 1)
    figs = C.resize((W, H), Image.LANCZOS)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sh.putalpha(figs.getchannel("A").filter(ImageFilter.GaussianBlur(26)).point(lambda v: v // 2))
    out.alpha_composite(sh, (12, 18))
    if rim:
        g = Image.new("RGBA", (W, H), CY + (0,)); g.putalpha(figs.getchannel("A").filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(12)).point(lambda v: int(v * 0.8)))
        out.alpha_composite(g)
    out.alpha_composite(figs)
    return out
