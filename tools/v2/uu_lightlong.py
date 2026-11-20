#!/usr/bin/env python3
"""Light-theme 16:9 long-form scenes (bright paper, dark ink, white cards). Used with "format": "long" and a light theme
such as "pharma".   usage: uu_lightlong.py spec.json still t1,t2 | full

Scene types (all prefixed ll_): hook, globe, stat, photo, date, notice, quote, law, price, pills, stamp, court, doc, chart,
donut, people, outro. Any scene may carry "chap": "NN · TITLE" (a chapter title card for the first ~2.6 s, then a small tag).
"""
import math, os, json
from PIL import Image, ImageDraw, ImageFilter
import uu_render as R
import uu_story as S
from uu_render import W, H, T, F, clamp, ease, back, prog, text_a, rect_a, paste_a, typed, fit_font, chrome

INK = (22, 30, 40); MUT = (92, 102, 112); TEAL = (0, 140, 130); SAFF = (240, 120, 20); GRN = (19, 136, 8); RED = (214, 48, 60)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
card = S.card; pill = S.pill

def chap(img, sc, t):
    """Chapter title: big for the first 2.6 s, then a small tag under the header."""
    c = sc.get("chap")
    if not c: return
    num, _, title = c.partition(" · ")
    if t < 2.8:
        a = clamp(t / 0.3) * (1 - clamp((t - 2.4) / 0.4))
        rect_a(img, (0, 0, W, H), (246, 248, 245), 0.9 * a)
        text_a(img, (W / 2, 420), "CHAPTER " + num, F("mono", 40), TEAL, a, "mm")
        q = back(clamp((t - 0.15) / 0.5)); f = fit_font("anton", int(150 * clamp(q, 0.4, 1.05)), title, W - 240)
        text_a(img, (W / 2, 560), title, f, INK, a, "mm", shadow=6)
        rect_a(img, (W / 2 - 160 * ease(clamp(t / 0.8)), 660, W / 2 + 160 * ease(clamp(t / 0.8)), 670), SAFF, a, 5)
    a = clamp((t - 2.6) / 0.4)
    if a > 0:
        s = num + " · " + title; f = F("mono", 24); w = ImageDraw.Draw(img).textlength(s, font=f)
        rect_a(img, (56, 120, 56 + w + 40, 162), (255, 255, 255), 0.9 * a, 21, TEAL, 2)
        text_a(img, (76, 141), s, f, TEAL, a, "lm")

def left_text(img, sc, t, x=110, y=300, w=760):
    """Kicker (typed), big line, then text lines, on the left half."""
    if sc.get("kicker"): text_a(img, (x, y), typed(sc["kicker"], prog(t, 0.3, 0.8)), F("mono", 30), TEAL, 1)
    if sc.get("big"):
        q = back(clamp((t - 0.6) / 0.5)); f = fit_font("anton", int(150 * clamp(q, 0.4, 1.05)), sc["big"], w)
        text_a(img, (x - 4, y + 60), sc["big"], f, sc.get("big_col") and tuple(sc["big_col"]) or INK, clamp((t - 0.6) / 0.25), shadow=6)
    for i, ln in enumerate(sc.get("lines", [])):
        st = 1.1 + i * 0.5
        text_a(img, (x, y + 270 + i * 66), typed(ln, prog(t, st, 0.8)), fit_font("disp", 48, ln, w, "Bold"), INK if i == 0 else MUT, 1)

def fin(img, sc, t, tg):
    chrome(img, tg); chap(img, sc, t)

# ---------------------------------------------------------------- scenes
def ll_hook(img, sc, t, D, tg, k):
    base = 930; hit = sc.get("hit_at", 3.5)
    shake = 14 * math.exp(-(t - hit) * 2.5) * math.sin((t - hit) * 40) if t > hit else 0
    lean = clamp((t - hit) / 1.2) * 5
    for i in range(6):
        x = 1060 + i * 128; h = 420 + (i * 137) % 260; a = clamp((t - 0.1 * i) / 0.4)
        lay = Image.new("RGBA", (140, h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.rectangle([5, 10, 132, h + 19], fill=(84, 98, 118, 255)); d.rectangle([5, 10, 132, 40], fill=(62, 74, 92, 255))
        for r_ in range(int((h - 60) / 54)):
            for c in range(3): d.rectangle([22 + c * 38, 60 + r_ * 54, 44 + c * 38, 90 + r_ * 54], fill=(200, 216, 232, 255) if (r_ + c + i) % 4 else (255, 214, 120, 255))
        lay = lay.rotate(-lean * (1 + i * 0.2), center=(70, h + 20), resample=Image.BICUBIC)
        paste_a(img, lay, (x + shake, base - h - 20), a)
    ba = clamp((t - 0.6) / 0.4); rect_a(img, (1180, 760, 1700, 840), (40, 50, 64), 0.95 * ba, 16)
    text_a(img, (1440, 800), "BIG PHARMA", F("anton", 64), (255, 255, 255), ba, "mm")
    p = pill(340, 136, SAFF, GRN, band=(255, 255, 255))
    if t < hit - 0.9: x, y, ang = 560, base - 80 + 6 * math.sin(tg * 3), 0
    else:
        q = clamp((t - (hit - 0.9)) / 0.9); x = 560 + 440 * ease(q); y = base - 80 - 300 * math.sin(q * math.pi) * (1 - q * 0.3); ang = -360 * ease(q)
        if t > hit: x, y, ang = 1000 - 60 * clamp((t - hit) / 0.5), base - 80, 0
    pr = p.rotate(ang, expand=True, resample=Image.BICUBIC); paste_a(img, pr, (x - pr.width / 2, y - pr.height / 2), clamp(t / 0.3))
    text_a(img, (560, base + 50), "1 INDIAN COMPANY", F("disp", 36, "Black"), SAFF, clamp((t - 0.8) / 0.4), "mm")
    for i, s in enumerate(sc.get("title", [])):
        ta = 0.5 + i * 0.4; q = back(clamp((t - ta) / 0.45))
        text_a(img, (110, 250 + i * 130), s, fit_font("anton", int(120 * clamp(q, 0.3, 1.1)), s, 900), INK if i == 0 else SAFF, clamp((t - ta) / 0.25), shadow=6)
    fin(img, sc, t, tg)

def ll_globe(img, sc, t, D, tg, k):
    lat, lon = sc.get("view", [0, 20]); lon += t * 1.5
    g = R.GLOBE.render(lat, lon, highlight=sc.get("highlight"), hl_alpha=clamp((t - 1.0) / 0.8), dim_others=0.2, pulse=0.5 + 0.5 * math.sin(tg * 3), hide=True)
    paste_a(img, g, (1400 - g.width / 2, 560 - g.height / 2), clamp(t / 0.5))
    left_text(img, sc, t); fin(img, sc, t, tg)

def tag_icon(img, x, y, s, a):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.polygon([(x, y + 120 * s), (x + 90 * s, y), (x + 420 * s, y), (x + 420 * s, y + 240 * s), (x + 90 * s, y + 240 * s)], fill=(255, 236, 200, 255), outline=(200, 160, 100, 255))
    d.ellipse([x + 40 * s, y + 100 * s, x + 80 * s, y + 140 * s], fill=(246, 248, 245, 255), outline=(200, 160, 100, 255), width=3)
    d.text((x + 250 * s, y + 120 * s), "$$$", font=F("anton", int(120 * s)), fill=RED + (255,), anchor="mm")
    lay = lay.rotate(8 * math.sin(t_glob[0] * 2) , center=(x, y), resample=Image.BICUBIC); paste_a(img, lay, (0, 0), a)
t_glob = [0.0]

def ll_stat(img, sc, t, D, tg, k):
    t_glob[0] = t
    tag_icon(img, 1200, 330, 1.2, clamp((t - 0.3) / 0.4))
    left_text(img, sc, t); fin(img, sc, t, tg)

def kenburns(path, w, h, t, D):
    p = os.path.join(ROOT, path)
    if not os.path.exists(p): return None
    im = Image.open(p).convert("RGB"); s = max(w / im.width, h / im.height) * (1.06 + 0.06 * t / max(D, 1))
    im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    ox = (im.width - w) * (0.5 + 0.3 * (t / max(D, 1) - 0.5)); oy = (im.height - h) / 2
    return im.crop((int(ox), int(oy), int(ox) + w, int(oy) + h)).convert("RGBA")

CRED = {}
def credit_for(path):
    d = os.path.dirname(path); f = os.path.basename(path)
    if d not in CRED:
        try: CRED[d] = json.load(open(os.path.join(ROOT, d, "credits.json")))
        except Exception: CRED[d] = {}
    c = CRED[d].get(f, {}) if isinstance(CRED[d], dict) else {}
    return " · ".join(x for x in (c.get("artist", ""), c.get("license", "")) if x)[:90]

def ll_photo(img, sc, t, D, tg, k):
    x0, y0, x1, y1 = 960, 190, W - 90, 960; a = clamp(t / 0.4)
    ph = kenburns(sc.get("img", ""), x1 - x0, y1 - y0, t, D)
    card(img, (x0 - 14, y0 - 14, x1 + 14, y1 + 14), a, 30)
    if ph is not None:
        m = Image.new("L", ph.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, ph.width - 1, ph.height - 1], 22, fill=255); ph.putalpha(m)
        paste_a(img, ph, (x0, y0), a)
        cr = credit_for(sc["img"])
        if cr: text_a(img, (x1 - 10, y1 + 34), "Photo: " + cr, F("inter", 18), MUT, a, "rm")
    left_text(img, sc, t, w=780); fin(img, sc, t, tg)

def ll_date(img, sc, t, D, tg, k):
    d_, m_, y_ = sc["date"]; a = clamp((t - 0.2) / 0.3); q = back(clamp((t - 0.2) / 0.6))
    x0, y0 = 220, 240
    card(img, (x0, y0, x0 + 520, y0 + 600), a, 34)
    rect_a(img, (x0, y0, x0 + 520, y0 + 130), RED, a, 34); rect_a(img, (x0, y0 + 80, x0 + 520, y0 + 130), RED, a, 0)
    text_a(img, (x0 + 260, y0 + 68), m_, F("anton", 76), (255, 255, 255), a, "mm")
    text_a(img, (x0 + 260, y0 + 330), d_, F("anton", int(260 * clamp(q, 0.4, 1.05))), INK, a, "mm")
    text_a(img, (x0 + 260, y0 + 520), y_, F("anton", 92), TEAL, a, "mm")
    for j in range(2): rect_a(img, (x0 + 120 + j * 250, y0 - 30, x0 + 150 + j * 250, y0 + 40), (120, 128, 136), a, 10)
    la = 1.0; text_a(img, (860, 460), typed(sc.get("label", ""), prog(t, la, 1.0)), fit_font("anton", 84, sc.get("label", ""), 980), INK, 1, shadow=4)
    if sc.get("sub"): text_a(img, (864, 580), sc["sub"], fit_font("disp", 44, sc["sub"], 960, "Bold"), MUT, clamp((t - 1.8) / 0.4))
    fin(img, sc, t, tg)

def ll_notice(img, sc, t, D, tg, k):
    a = clamp((t - 0.3) / 0.3); x0, y0 = 1080, 230
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); card(lay, (x0, y0, x0 + 620, y0 + 700), 1, 10)
    d = ImageDraw.Draw(lay); d.text((x0 + 310, y0 + 80), "LEGAL NOTICE", font=F("anton", 64), fill=INK + (255,), anchor="mm")
    for j in range(9): d.rounded_rectangle([x0 + 60, y0 + 170 + j * 50, x0 + 560 - (j % 3) * 70, y0 + 186 + j * 50], 8, fill=(214, 222, 226, 255))
    d.ellipse([x0 + 420, y0 + 560, x0 + 560, y0 + 690], outline=RED + (255,), width=8)
    lay = lay.rotate(4 * (1 - ease(clamp(t / 0.8))) + 3, center=(x0 + 310, y0 + 350), resample=Image.BICUBIC); paste_a(img, lay, (0, 60 * (1 - ease(clamp(t / 0.7)))), a)
    sc2 = dict(sc); sc2["big"] = sc.get("title"); left_text(img, sc2, t); fin(img, sc, t, tg)

def ll_quote(img, sc, t, D, tg, k):
    a = clamp((t - 0.2) / 0.4); card(img, (180, 230, W - 180, 860), a, 34)
    text_a(img, (260, 260), "“", F("anton", 260), SAFF, a)
    for i, ln in enumerate(sc["quote"]):
        text_a(img, (W / 2, 430 + i * 110), typed(ln, prog(t, 0.6 + i * 0.9, 1.0)), fit_font("disp", 78, ln, W - 520, "Black"), INK, 1, "mm")
    text_a(img, (W / 2, 790), "— " + sc.get("who", ""), F("inter", 34, "SemiBold"), MUT, clamp((t - 3.0) / 0.5), "mm")
    fin(img, sc, t, tg)

def ll_law(img, sc, t, D, tg, k):
    for i, (title, sub, closed, col) in enumerate(sc["cards"]):
        col = tuple(col); ca = sc.get("card_at", [0.5, 2.2])[i]; a = clamp((t - ca) / 0.4); x0 = 150 + i * 830
        if a <= 0: continue
        card(img, (x0, 300 + 40 * (1 - ease(a)), x0 + 790, 860 + 40 * (1 - ease(a))), a, 30)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); S.lock(ImageDraw.Draw(lay), x0 + 395, 380, 2.0, closed, col); paste_a(img, lay, (0, 0), a)
        text_a(img, (x0 + 395, 640), title, fit_font("anton", 70, title, 700), INK, a, "mm")
        for j, ln in enumerate(sub): text_a(img, (x0 + 395, 730 + j * 56), ln, fit_font("inter", 40, ln, 720, "SemiBold"), col, a, "mm")
    fin(img, sc, t, tg)

def ll_price(img, sc, t, D, tg, k):
    steps = sc["steps"]; ats = sc.get("step_at", [0.4, D * 0.3])
    text_a(img, (W / 2, 220), typed(sc.get("kicker", ""), prog(t, 0.2, 0.8)), F("mono", 32), TEAL, 1, "mm")
    for i, (lab, val) in enumerate(steps):
        a = clamp((t - ats[i]) / 0.4); x = W / 2 + (i - (len(steps) - 1) / 2) * 760
        if a <= 0: continue
        old = i < len(steps) - 1 and t > ats[i + 1] + 0.3
        card(img, (x - 330, 320, x + 330, 760), a, 30, outline=TEAL if not old and i else None)
        text_a(img, (x, 400), lab, fit_font("disp", 40, lab, 600, "Black"), MUT if old else (TEAL if i else INK), a, "mm")
        q = back(clamp((t - ats[i]) / 0.5))
        text_a(img, (x, 580), val, F("anton", int(200 * clamp(q, 0.4, 1.05))), (150, 158, 166) if old else (TEAL if i else RED), a, "mm", shadow=6)
        if old:
            s = ease(clamp((t - ats[i + 1] - 0.3) / 0.4)); d = ImageDraw.Draw(img); d.line([x - 250, 620, x - 250 + 500 * s, 540], fill=RED + (255,), width=14)
    if len(steps) > 1 and t > ats[1]:
        a = clamp((t - ats[1]) / 0.4); d = ImageDraw.Draw(img); d.line([W / 2 - 40, 540, W / 2 + 40, 540], fill=SAFF + (int(255 * a),), width=10)
        d.polygon([(W / 2 + 40, 520), (W / 2 + 70, 540), (W / 2 + 40, 560)], fill=SAFF + (int(255 * a),))
    if sc.get("silence") and t > D * 0.45:
        a = clamp((t - D * 0.45) / 0.6); text_a(img, (W / 2, 880), "…silence. No takers.", F("disp", 56, "Black"), MUT, a, "mm")
    if sc.get("chip") and t > sc.get("chip_at", D * 0.55):
        a = clamp((t - sc.get("chip_at", D * 0.55)) / 0.4); s = sc["chip"]; f = F("disp", 60, "Black"); w = ImageDraw.Draw(img).textlength(s, font=f)
        rect_a(img, (W / 2 - w / 2 - 44, 830, W / 2 + w / 2 + 44, 940), SAFF, a, 55); text_a(img, (W / 2, 885), s, f, (255, 255, 255), a, "mm")
    fin(img, sc, t, tg)

def ll_pills(img, sc, t, D, tg, k):
    names = sc.get("names"); cols = [((90, 140, 220), (60, 110, 200)), ((240, 170, 40), (226, 140, 20)), ((120, 190, 120), (80, 160, 90))]
    ma = sc.get("merge_at", D * 0.35); m = ease(clamp((t - ma) / 0.9))
    for i in range(3):
        a = clamp((t - 0.3 - i * 0.35) / 0.3); y0 = 300 + i * 200; y = y0 + (500 - y0) * m
        p = pill(440, 150, *cols[i], label=names[i]); paste_a(img, p, (1340 - 220, y - 75), a * (1 - clamp((t - ma - 0.7) / 0.3)))
    if t > ma + 0.6:
        q = back(clamp((t - ma - 0.6) / 0.6)); s = clamp(q, 0.3, 1.15); p = pill(int(600 * s), int(210 * s), TEAL, (0, 110, 104), label=sc.get("result", "3-IN-1"))
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(glow).ellipse([960, 300, 1720, 720], fill=TEAL + (int(70 * clamp(q, 0, 1)),))
        img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(60))); paste_a(img, p, (1340 - p.width / 2, 500 - p.height / 2), 1)
    sc2 = dict(sc); sc2["kicker"] = "CIPLA · 2001"; sc2["big"] = "3 → 1"; left_text(img, sc2, t); fin(img, sc, t, tg)

def ll_stamp(img, sc, t, D, tg, k):
    pa = sc.get("stamp_at", 0.8); q = back(clamp((t - pa) / 0.4)); s = clamp(q, 0.3, 1.25)
    lay = Image.new("RGBA", (760, 260), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.rounded_rectangle([8, 8, 752, 252], 30, outline=RED + (255,), width=14); ld.text((380, 130), sc.get("stamp", ""), font=F("anton", 150), fill=RED + (255,), anchor="mm")
    lay = lay.rotate(-7, expand=True, resample=Image.BICUBIC); lay = lay.resize((int(lay.width * s), int(lay.height * s)), Image.LANCZOS)
    paste_a(img, lay, (1340 - lay.width / 2, 520 - lay.height / 2), clamp((t - pa) / 0.15))
    left_text(img, sc, t, w=780); fin(img, sc, t, tg)

def ll_court(img, sc, t, D, tg, k):
    text_a(img, (110, 250), typed(sc.get("kicker", ""), prog(t, 0.2, 1.0)), F("mono", 30), TEAL, 1)
    da = sc.get("drop_at", D * 0.62); n = sc.get("n", 39)
    for i in range(n):
        r_, c = divmod(i, 13); x = 110 + c * 92; y = 330 + r_ * 104; a = clamp((t - 0.4 - i * 0.03) / 0.2)
        if t > da:
            q = clamp((t - da - (i % 13) * 0.04) / 0.6); y += 600 * q * q; a *= 1 - q
        if a <= 0: continue
        rect_a(img, (x, y, x + 76, y + 84), (84, 98, 118), a, 10)
        for wy in range(2):
            for wx in range(3): rect_a(img, (x + 10 + wx * 21, y + 14 + wy * 30, x + 23 + wx * 21, y + 34 + wy * 30), (200, 216, 232), a, 2)
    a = clamp((t - 1.0) / 0.4); card(img, (1400, 360, 1820, 520), a); text_a(img, (1610, 440), sc.get("vs", ""), F("disp", 48, "Black"), INK, a, "mm")
    if t > da + 0.5:
        q = back(clamp((t - da - 0.5) / 0.5)); a = clamp((t - da - 0.5) / 0.3)
        text_a(img, (W / 2, 720), sc.get("result", ""), F("anton", int(150 * clamp(q, 0.3, 1.1))), TEAL, a, "mm", shadow=6)
        text_a(img, (W / 2, 850), sc.get("date", ""), F("mono", 40), MUT, a, "mm")
    fin(img, sc, t, tg)

def ll_doc(img, sc, t, D, tg, k):
    a = clamp((t - 0.2) / 0.4); x0, y0 = 560, 200
    card(img, (x0, y0, x0 + 800, y0 + 760), a, 12, fill=(255, 252, 240))
    text_a(img, (x0 + 400, y0 + 80), "WORLD TRADE ORGANIZATION", F("mono", 28), MUT, a, "mm")
    text_a(img, (x0 + 400, y0 + 160), sc.get("title", ""), F("anton", 76), INK, a, "mm")
    text_a(img, (x0 + 400, y0 + 240), sc.get("date", ""), F("disp", 36, "Bold"), TEAL, a, "mm")
    d = ImageDraw.Draw(img)
    for j in range(8): d.rounded_rectangle([x0 + 80, y0 + 310 + j * 44, x0 + 720 - (j % 3) * 60, y0 + 324 + j * 44], 7, fill=(220, 224, 214, int(255 * a)))
    ha = sc.get("hl_at", D * 0.45); q = ease(clamp((t - ha) / 0.6))
    if q > 0:
        rect_a(img, (x0 + 60, y0 + 560, x0 + 60 + 680 * q, y0 + 690), (255, 226, 120), 0.85, 8)
        ln = sc.get("line", ""); parts = [ln[:len(ln) // 2].rsplit(" ", 1)[0], ""]; parts[1] = ln[len(parts[0]):].strip()
        for j, p in enumerate(parts): text_a(img, (x0 + 400, y0 + 595 + j * 56), p, fit_font("inter", 34, p, 660, "Bold"), INK, clamp((t - ha) / 0.4), "mm")
    fin(img, sc, t, tg)

def ll_chart(img, sc, t, D, tg, k):
    text_a(img, (W / 2, 220), sc.get("title", ""), fit_font("disp", 54, sc.get("title", ""), W - 300, "Black"), INK, clamp(t / 0.3), "mm")
    card(img, (200, 280, W - 200, 960), clamp(t / 0.3))
    bars = sc["bars"]; mx = max(b[1] for b in bars); ats = sc.get("bar_at", [0.6 + i * D * 0.17 for i in range(len(bars))])
    base, top, bw = 860, 380, 230
    for i, (lab, v, vs) in enumerate(bars):
        x = 330 + i * 340; g = ease(clamp((t - ats[i]) / 0.9)); a = clamp((t - ats[i]) / 0.3)
        if a <= 0: continue
        h = max(10, (base - top) * v / mx * g); col = RED if i == 0 else TEAL
        rect_a(img, (x, base - h, x + bw, base), col, a, 14)
        text_a(img, (x + bw / 2, base - h - 46), vs, F("anton", 64), col, a, "mm")
        text_a(img, (x + bw / 2, base + 50), lab, F("disp", 40, "Black"), INK, a, "mm")
    if sc.get("note") and t > ats[-1] + 1.0:
        text_a(img, (W - 260, 420), sc["note"], F("disp", 52, "Black"), SAFF, clamp((t - ats[-1] - 1.0) / 0.4), "rm")
    fin(img, sc, t, tg)

def donut(img, cx, cy, r, share, g, a, col, label, big):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(226, 232, 236, 255)); d.pieslice([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * share * g, fill=col + (255,))
    d.ellipse([cx - r * 0.62, cy - r * 0.62, cx + r * 0.62, cy + r * 0.62], fill=(255, 255, 255, 255)); paste_a(img, lay, (0, 0), a)
    text_a(img, (cx, cy), f"{round(share * 100 * g)}%", F("anton", int(r * 0.5)), col, a, "mm")
    text_a(img, (cx, cy + r + 60), label, fit_font("disp", 40, label, 640, "Black"), INK, a, "mm")

def ll_donut(img, sc, t, D, tg, k):
    text_a(img, (W / 2, 220), typed(sc.get("kicker", ""), prog(t, 0.2, 0.8)), F("mono", 32), TEAL, 1, "mm")
    card(img, (160, 280, W - 160, 980), clamp(t / 0.3))
    donut(img, 620, 580, 220, sc["share"], ease(clamp((t - 0.6) / 1.6)), clamp(t / 0.3), SAFF, sc.get("label", ""), True)
    a2 = sc.get("second_at", D * 0.45)
    if t > a2: donut(img, 1300, 580, 220, sc["share2"], ease(clamp((t - a2) / 1.4)), clamp((t - a2) / 0.3), GRN, sc.get("label2", ""), True)
    paste_a(img, R.flag("IN", 90), (620 - 45, 350), clamp(t / 0.3))
    fin(img, sc, t, tg)

def ll_people(img, sc, t, D, tg, k):
    a = clamp(t / 0.3); card(img, (900, 220, W - 110, 960), a)
    n0, n1 = sc["from"], sc["to"]; g = ease(clamp((t - sc.get("grow_at", 1.0)) / 2.4)); v = n0 + (n1 - n0) * g
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for i in range(int(round(n1))):
        r_, c = divmod(i, 8); x = 990 + c * 105; y = 270 + r_ * 160
        col = (0, 110, 104) if i < int(round(n0)) else (TEAL if i < int(v) else (214, 222, 226)); S.person_icon(d, x, y, 1.15, col)
    paste_a(img, lay, (0, 0), a)
    text_a(img, (110, 380), f"{v:.1f}", F("anton", 230), TEAL, clamp((t - 0.5) / 0.3), shadow=6)
    text_a(img, (116, 660), sc.get("label", ""), fit_font("disp", 52, sc.get("label", ""), 760, "Black"), INK, clamp((t - 0.8) / 0.4))
    text_a(img, (116, 740), sc.get("sub", ""), fit_font("inter", 34, sc.get("sub", ""), 760, "SemiBold"), MUT, clamp((t - 1.2) / 0.4))
    fin(img, sc, t, tg)

def ll_outro(img, sc, t, D, tg, k):
    g = R.GLOBE.render(18, 75 + t * 3, highlight=["IN"], hl_alpha=0.9, dim_others=0.2, pulse=0.5 + 0.5 * math.sin(tg * 4))
    paste_a(img, g, (1400 - g.width / 2, 520 - g.height / 2), clamp(t / 0.5))
    for i, ln in enumerate(sc.get("lines", [])):
        text_a(img, (110, 300 + i * 100), typed(ln, prog(t, 0.4 + i * 1.0, 1.0)), fit_font("disp", 62, ln, 900, "Black"), TEAL if i == len(sc["lines"]) - 1 else INK, 1)
    ca = max(2.5, D - 6.0); a = clamp((t - ca) / 0.5)
    if a > 0:
        card(img, (110, 700, 900, 900), a); paste_a(img, R.LOGO.resize((120, 120), Image.LANCZOS), (140, 740), a)
        text_a(img, (290, 770), "UNKNOWN UNCOVERED", F("disp", 44, "Black"), INK, a, "lm")
        rect_a(img, (290, 815, 520, 875), (230, 30, 40), a, 30); text_a(img, (405, 845), "SUBSCRIBE", F("disp", 30, "Black"), (255, 255, 255), a, "mm")
        rect_a(img, (540, 815, 760, 875), (255, 255, 255), a, 30, INK, 3); text_a(img, (650, 845), "FOLLOW", F("disp", 30, "Black"), INK, a, "mm")
    chrome(img, tg)

R.SCENE_FN.update({k: v for k, v in globals().items() if k.startswith("ll_") and callable(v)})

if __name__ == "__main__":
    R.main()
