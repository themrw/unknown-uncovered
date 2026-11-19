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


# ---------------------------------------------------------------- reel 017: Raju's tea stall (a fictional character)
VEST = (238, 232, 214, 255); VEST_D = (200, 192, 170, 255); WOOD = (122, 78, 44, 255); WOOD_D = (92, 56, 30, 255)
STRIPE_A = (230, 150, 40, 255); STRIPE_B = (250, 244, 228, 255); STEEL = (176, 180, 186, 255); GLASS = (210, 150, 80, 230)

def stall_layer(W, H, cx, base, u, props=(), qr_img=None):
    """Raju behind his tea counter. props: coins, qr, soundbox. Static layer; animate steam/pulses on top."""
    K = 2; C = Image.new("RGBA", (W * K, H * K), (0, 0, 0, 0)); cd = ImageDraw.Draw(C); OW = 5 * K
    def E(box, fill, w=OW): cd.ellipse([v * K for v in box], fill=fill, outline=INK, width=w)
    def P(pts, fill, w=OW): cd.polygon([(x * K, y * K) for x, y in pts], fill=fill, outline=INK, width=w)
    def RR(box, r, fill, w=OW): cd.rounded_rectangle([v * K for v in box], r * K, fill=fill, outline=INK, width=w)
    def L(pts, fill=INK, w=OW): cd.line([(x * K, y * K) for x, y in pts], fill=fill, width=w, joint="curve")
    def A(box, a0, a1, fill=INK, w=OW): cd.arc([v * K for v in box], a0, a1, fill=fill, width=w)
    top = base - 150 * u; ct = base - 46 * u
    for sx in (-1, 1): RR([cx + sx * 74 * u - 3 * u, top, cx + sx * 74 * u + 3 * u, base], 1 * u, WOOD_D)      # poles
    # Raju (behind the counter)
    hy = base - 104 * u
    P([(cx - 22 * u, ct + 2 * u), (cx - 20 * u, base - 80 * u), (cx - 9 * u, base - 87 * u), (cx + 9 * u, base - 87 * u),
       (cx + 20 * u, base - 80 * u), (cx + 22 * u, ct + 2 * u)], VEST)
    P([(cx - 20 * u, base - 80 * u), (cx - 30 * u, base - 62 * u), (cx - 25 * u, ct + 2 * u), (cx - 18 * u, base - 66 * u)], VEST_D)
    P([(cx + 20 * u, base - 80 * u), (cx + 30 * u, base - 62 * u), (cx + 25 * u, ct + 2 * u), (cx + 18 * u, base - 66 * u)], VEST_D)
    P([(cx - 12 * u, base - 86 * u), (cx - 4 * u, base - 86 * u), (cx + 10 * u, base - 55 * u), (cx + 3 * u, base - 52 * u)], (200, 52, 48, 255))  # gamchha
    E([cx - 5 * u, base - 92 * u, cx + 5 * u, base - 84 * u], SKIN)                                                  # neck
    E([cx - 13.5 * u, hy - 2 * u, cx - 9 * u, hy + 5 * u], SKIN); E([cx + 9 * u, hy - 2 * u, cx + 13.5 * u, hy + 5 * u], SKIN)
    E([cx - 11 * u, hy - 12 * u, cx + 11 * u, hy + 12 * u], SKIN)
    P([(cx - 11.5 * u, hy - 2 * u), (cx - 11 * u, hy - 10 * u), (cx - 4 * u, hy - 15 * u), (cx + 6 * u, hy - 14 * u), (cx + 11.5 * u, hy - 6 * u),
       (cx + 11.5 * u, hy - 1 * u), (cx + 8 * u, hy - 8 * u), (cx - 8 * u, hy - 8 * u)], HAIR)
    for sx in (-1, 1):
        E([cx + sx * 4.5 * u - 1.6 * u, hy - 1.5 * u, cx + sx * 4.5 * u + 1.6 * u, hy + 1.7 * u], INK, OW // 3)
        L([(cx + sx * 2.5 * u, hy - 4.2 * u), (cx + sx * 7 * u, hy - 4.8 * u)], INK, OW // 2)
    P([(cx - 7 * u, hy + 5.5 * u), (cx, hy + 3.8 * u), (cx + 7 * u, hy + 5.5 * u), (cx + 5 * u, hy + 7.5 * u), (cx, hy + 6 * u), (cx - 5 * u, hy + 7.5 * u)], HAIR, OW // 2)
    A([cx - 4 * u, hy + 4 * u, cx + 4 * u, hy + 10 * u], 20, 160, INK, OW // 2)                                       # smile
    # counter
    RR([cx - 70 * u, ct, cx + 70 * u, base], 2 * u, WOOD)
    for k in range(1, 4): L([(cx - 70 * u, ct + k * 11.5 * u), (cx + 70 * u, ct + k * 11.5 * u)], WOOD_D, OW // 2)
    RR([cx - 74 * u, ct - 3 * u, cx + 74 * u, ct + 2 * u], 1 * u, WOOD_D)
    RR([cx - 40 * u, ct + 12 * u, cx + 40 * u, ct + 32 * u], 2 * u, (250, 232, 170, 255))                            # sign board (text drawn by scene)
    # arms resting on the counter
    for sx in (-1, 1):
        P([(cx + sx * 22 * u, base - 78 * u), (cx + sx * 28 * u, base - 74 * u), (cx + sx * 26 * u, ct - 2 * u), (cx + sx * 18 * u, ct - 2 * u)], SKIN)
        E([cx + sx * 22 * u - 5 * u, ct - 6 * u, cx + sx * 22 * u + 5 * u, ct + 1 * u], SKIN)
    # stove + kettle (left), glasses (right)
    RR([cx - 64 * u, ct - 8 * u, cx - 44 * u, ct - 3 * u], 1 * u, (60, 60, 64, 255))
    E([cx - 62 * u, ct - 24 * u, cx - 46 * u, ct - 7 * u], STEEL); L([(cx - 46 * u, ct - 18 * u), (cx - 40 * u, ct - 22 * u)], INK, OW)
    A([cx - 59 * u, ct - 30 * u, cx - 49 * u, ct - 20 * u], 180, 360, INK, OW // 2)
    for j in range(4):
        x = cx + 36 * u + j * 8 * u
        P([(x, ct - 12 * u), (x + 5.5 * u, ct - 12 * u), (x + 4.8 * u, ct - 3 * u), (x + 0.7 * u, ct - 3 * u)], GLASS, OW // 2)
    if "coins" in props:
        for j, (dx, dy) in enumerate([(-30, -4), (-24, -3), (-27, -6), (14, -4), (20, -3)]):
            E([cx + dx * u - 3 * u, ct + dy * u - 1.6 * u, cx + dx * u + 3 * u, ct + dy * u + 1.6 * u], (226, 186, 72, 255), OW // 2)
    if "qr" in props and qr_img is not None:
        RR([cx + 6 * u, ct - 30 * u, cx + 30 * u, ct - 2 * u], 2 * u, (255, 255, 255, 255))
        q = qr_img(15, int(20 * u * K), 5); C.alpha_composite(q, (int((cx + 8 * u) * K), int((ct - 28 * u) * K)))
        L([(cx + 18 * u, ct - 2 * u), (cx + 18 * u, ct)], INK, OW)
    if "soundbox" in props:
        RR([cx - 38 * u, ct - 16 * u, cx - 26 * u, ct - 1 * u], 3 * u, (30, 40, 70, 255))
        for k in range(3): E([cx - 34.5 * u + k * 2.8 * u, ct - 11 * u, cx - 33 * u + k * 2.8 * u, ct - 9.5 * u], (200, 210, 230, 255), 1)
    # awning
    n = 9; w = 160 * u / n
    for j in range(n):
        x0 = cx - 80 * u + j * w
        P([(x0, top), (x0 + w, top), (x0 + w + 1 * u, top + 16 * u), (x0 - 1 * u, top + 16 * u)], STRIPE_A if j % 2 == 0 else STRIPE_B)
        A([x0 - 1 * u, top + 10 * u, x0 + w + 1 * u, top + 22 * u], 0, 180, INK, OW // 2)
    C = C.resize((W, H), Image.LANCZOS)
    rim = C.getchannel("A").filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(10))
    glow = Image.new("RGBA", (W, H), (255, 190, 90, 0)); glow.putalpha(rim.point(lambda v: int(v * 0.45)))
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0)); out.alpha_composite(glow); out.alpha_composite(C)
    return out

def eiffel_card(w, h, qr_img=None):
    """A phone photo: the Eiffel Tower at dusk and a girl scanning a UPI QR stand (illustration)."""
    K = 2; C = Image.new("RGBA", (w * K, h * K), (0, 0, 0, 0)); d = ImageDraw.Draw(C)
    for y in range(h * K):
        f = y / (h * K); d.line([(0, y), (w * K, y)], fill=(int(40 + 180 * f), int(50 + 90 * f), int(110 - 30 * f), 255))
    cx = w * 0.62 * K; b = h * 0.86 * K; tw = w * 0.42 * K; th = h * 0.78 * K
    dk = (34, 28, 40, 255)
    d.polygon([(cx - tw / 2, b), (cx - tw * 0.06, b - th), (cx + tw * 0.06, b - th), (cx + tw / 2, b)], fill=dk)
    d.polygon([(cx - tw * 0.3, b), (cx, b - th * 0.22), (cx + tw * 0.3, b)], fill=(int(40 + 180 * 0.9), int(50 + 90 * 0.9), 90, 255))
    for f_, ww in ((0.35, 0.36), (0.62, 0.22)):
        y = b - th * f_; d.rectangle([cx - tw * ww / 2, y - 6 * K, cx + tw * ww / 2, y + 2 * K], fill=dk)
    d.line([(cx, b - th), (cx, b - th - 18 * K)], fill=dk, width=3 * K)
    for j in range(14):
        x = cx + (j - 7) * tw * 0.05; y = b - th * (0.05 + 0.06 * (j % 7))
        d.ellipse([x - 2 * K, y - 2 * K, x + 2 * K, y + 2 * K], fill=(255, 220, 140, 255))
    d.rectangle([0, b, w * K, h * K], fill=(30, 26, 34, 255))
    gx = w * 0.2 * K; gb = b                                                    # the girl (silhouette) + QR stand
    d.ellipse([gx - 9 * K, gb - 112 * K, gx + 9 * K, gb - 92 * K], fill=(26, 20, 26, 255))
    d.polygon([(gx - 13 * K, gb), (gx - 10 * K, gb - 92 * K), (gx + 10 * K, gb - 92 * K), (gx + 14 * K, gb)], fill=(150, 40, 70, 255))
    d.line([(gx + 8 * K, gb - 78 * K), (gx + 30 * K, gb - 84 * K)], fill=(26, 20, 26, 255), width=6 * K)
    d.rounded_rectangle([gx + 28 * K, gb - 94 * K, gx + 40 * K, gb - 74 * K], 3 * K, fill=(20, 20, 24, 255), outline=(255, 255, 255, 255), width=K)
    sx = gx + 62 * K; d.rectangle([sx - 2 * K, gb - 60 * K, sx + 2 * K, gb], fill=(60, 60, 66, 255))
    d.rounded_rectangle([sx - 22 * K, gb - 104 * K, sx + 22 * K, gb - 56 * K], 4 * K, fill=(255, 255, 255, 255))
    if qr_img is not None: C.alpha_composite(qr_img(15, 36 * K, 9), (int(sx - 18 * K), int(gb - 100 * K)))
    C = C.resize((w, h), Image.LANCZOS)
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], 18, fill=255); C.putalpha(m)
    return C
