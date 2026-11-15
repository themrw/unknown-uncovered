def s_title(img, t, D, tg):
    radar(img, W / 2, 1000, 500, tg, 0.55 * prog(t, 0, 0.8))
    chrome(img, tg, header=False)
    a = prog(t, 0.1, 0.5)
    rect_a(img, (80, 590, 80 + int(200 * a), 600), RED)
    text_a(img, (80, 620), typed("SIPRI DATA // 2021 → 2026", prog(t, 0.1, 0.8)), mono(30), HUD, 1)
    for i, (s, f, col, y, st) in enumerate([("THE SILENT", dfont("Black", 150), WHITE, 670, 0.3),
                                            ("NUCLEAR", dfont("Black", 170), AMBER, 840, 0.5),
                                            ("BUILD-UP", dfont("Black", 170), RED, 1020, 0.7)]):
        p = back((t - st) / 0.55); text_a(img, (80 - (1 - p) * 140, y), s, f, col, clamp((t - st) / 0.3))
    text_a(img, (80, 1270), typed("Who added the most warheads in 5 years?", prog(t, 1.3, 1.4)), font("Medium", 44), WHITE, 1)
    codes = ["CN", "IN", "KP", "PK", "GB"]
    for i, c in enumerate(codes):
        p = back((t - 2.2 - i * 0.1) / 0.45)
        paste_a(img, flag(c, 120), (80 + i * 140, 1400 + (1 - p) * 60), clamp((t - 2.2 - i * 0.1) / 0.25))

def s_global(img, t, D, tg):
    radar(img, W - 140, 760, 420, tg, 0.5 * prog(t, 0, 0.6))
    chrome(img, tg)
    text_a(img, (80, 380), typed("> NUCLEAR WARHEADS WORLDWIDE, JAN 2026", prog(t, 0.1, 0.9)), mono(30), HUD, 1)
    v = 12187 * prog(t, 0.3, 2.4)
    text_a(img, (80, 450), f"{int(v):,}", dfont("Black", 250), WHITE, prog(t, 0.2, 0.4))
    text_a(img, (80, 730), "WARHEADS", dfont("Black", 120), RED, clamp((t - 0.6) / 0.3))
    rect_a(img, (80, 880, 80 + int(920 * prog(t, 0.8, 1.2)), 884), RED)
    items = [("9,745", "in military stockpiles, ready for use"), ("+130", "added to stockpiles in one year"), ("9", "countries have nuclear weapons")]
    for i, (k, s) in enumerate(items):
        y = 960 + i * 190; st = 2.2 + i * 1.2; a = clamp((t - st) / 0.3); dx = (1 - back((t - st) / 0.5)) * -120
        rect_a(img, (80 + dx, y, 1000 + dx, y + 150), (14, 22, 22), a * 0.85, 14, HUD, 2)
        rect_a(img, (80 + dx, y, 92 + dx, y + 150), AMBER, a)
        text_a(img, (120 + dx, y + 18), k, dfont("Black", 64), WHITE, a)
        text_a(img, (120 + dx, y + 96), s, font("Medium", 38), MUTED, a)

# code, name, tag, label2021, start, end, endlabel, chip1, chip2 (label, value, colour), fact lines
C = [
 ("CN", "CHINA", "FASTEST GROWTH", "350", 350, 620, "~620", ("5-YEAR CHANGE", "+270", RED), ("GROWTH", "+77%", RED), ["Expanding faster than", "any other country"]),
 ("IN", "INDIA", "STEADY RISE", "156", 156, 190, "~190", ("5-YEAR CHANGE", "+34", RED), ("DEPLOYED", "12 on missiles", AMBER), ["First time SIPRI counts Indian", "warheads as deployed"]),
 ("KP", "NORTH KOREA", "ACCELERATING", "40–50", 45, 60, "~60", ("5-YEAR CHANGE", "+10 to 20", RED), ("MATERIAL FOR", "30+ more", AMBER), ["Speeding up fissile", "material production"]),
 ("PK", "PAKISTAN", "SLOW & STEADY", "165", 165, 170, "~170", ("5-YEAR CHANGE", "+5", RED), ("OUTLOOK", "May grow", AMBER), ["Building new delivery systems", "and fissile material"]),
 ("GB", "UNITED KINGDOM", "GONE QUIET", "225", 225, 225, "225", ("WARHEAD CAP", "180 → 260", RED), ("PUBLIC COUNT", "Stopped", AMBER), ["Raised its ceiling in 2021,", "then stopped publishing numbers"]),
]
MAXV = 620

def country_scene(idx):
    code, name, tag, l21, v0, v1, lbl, c1, c2, fact = C[idx]
    def s(img, t, D, tg):
        fx, fy, fw = W - 80 - 400, 380, 400; fh = int(fw * 128 / 136)
        radar(img, fx + fw / 2, fy + fh / 2 + 10, 300, tg, 0.6 * prog(t, 0, 0.5), speed=140)
        chrome(img, tg)
        for i in range(len(C)):
            rect_a(img, (80 + i * 46, 310, 80 + i * 46 + (34 if i == idx else 22), 318), RED if i == idx else (50, 62, 66), 1, 4)
        p = back((t - 0.05) / 0.5)
        text_a(img, (80, 380), f"#{idx+1}", dfont("Black", 150 + int(30 * (1 - p))), RED, clamp(t / 0.25))
        text_a(img, (84, 560), typed(tag, prog(t, 0.2, 0.6)), mono(28), HUD, 1)
        fa = clamp((t - 0.15) / 0.3); bob = 6 * math.sin(tg * 2.2)
        paste_a(img, flag(code, fw), (fx, fy + bob), fa)
        lk = ease((t - 0.3) / 0.6); pad = 20 + 90 * (1 - lk)
        brackets(img, (fx - pad, fy - pad + bob, fx + fw + pad, fy + fh + pad + bob), RED if lk < 1 else HUD, clamp((t - 0.3) / 0.2), 44, 5)
        if 0.3 < t < 1.6:
            sy = fy + fh * ((t - 0.3) / 1.3); rect_a(img, (fx - 10, sy, fx + fw + 10, sy + 4), HUD, 0.8)
        if lk >= 1:
            text_a(img, (fx + fw / 2, fy - 50), "● PROFILE LOADED", mono(24), HUD, clamp((t - 0.9) / 0.3), "mm")
        size = 110 if len(name) <= 10 else 84
        nm = typed(name, prog(t, 0.4, 0.7))
        text_a(img, (80, 760), nm, dfont("Black", size), WHITE, 1)
        if (len(nm) < len(name) or int(tg * 3) % 2 == 0) and 0.4 < t < 3:
            cx = 80 + ImageDraw.Draw(img).textlength(nm, font=dfont("Black", size)) + 10
            rect_a(img, (cx, 770, cx + 22, 770 + int(size * 0.75)), HUD, 1)
        text_a(img, (84, 900), f"2021:  {l21}   →   2026:", font("SemiBold", 40), MUTED, clamp((t - 0.6) / 0.3))
        g = prog(t, 0.9, 1.8)
        cur = int(round(v0 + (v1 - v0) * g))
        shown = lbl if g >= 0.999 else (("~" if lbl.startswith("~") else "") + str(cur))
        text_a(img, (80, 950), shown, dfont("Black", 220), WHITE, clamp((t - 0.6) / 0.3))
        text_a(img, (80 + ImageDraw.Draw(img).textlength(shown, font=dfont("Black", 220)) + 24, 1080), "WARHEADS", dfont("Black", 54), RED, clamp((t - 0.8) / 0.3))
        ba = clamp((t - 1.0) / 0.3); bw = 920
        rect_a(img, (80, 1215, 80 + bw, 1237), (24, 34, 36), ba, 8)
        base = int(46 * v0 / MAXV); tot = int(46 * v1 / MAXV); shown_segs = int(tot * prog(t, 1.0, 1.5))
        for k in range(shown_segs):
            rect_a(img, (80 + k * 20, 1217, 80 + k * 20 + 15, 1235), (120, 128, 134) if k < base else RED, ba, 2)
        text_a(img, (80, 1255), "Grey = 2021   Red = added since   (scale: China 2026)", font("Regular", 26), MUTED, ba)
        for j, (lab, v, col) in enumerate([c1, c2]):
            st = 1.5 + j * 0.25; ca = clamp((t - st) / 0.25); dy = (1 - back((t - st) / 0.5)) * 50; x = 80 + j * 470
            rect_a(img, (x, 1330 + dy, x + 440, 1480 + dy), (14, 22, 24), ca * 0.9, 18, HUD if j == 0 else col, 2)
            text_a(img, (x + 30, 1355 + dy), lab, mono(24), MUTED, ca)
            vf = dfont("Black", 60) if len(v) < 9 else dfont("Bold", 44)
            text_a(img, (x + 30, 1400 + dy), v, vf, col, ca)
        text_a(img, (80, 1530), typed(fact[0], prog(t, 2.1, 0.8)), font("SemiBold", 42), AMBER, 1)
        text_a(img, (80, 1582), typed(fact[1], prog(t, 2.7, 0.8)), font("SemiBold", 42), AMBER, 1)
    return s

JUMP = [("CN", "China", 270, "+270"), ("IN", "India", 34, "+34"), ("KP", "North Korea", 15, "+10–20"), ("PK", "Pakistan", 5, "+5")]
def s_jump(img, t, D, tg):
    radar(img, W - 60, 1100, 460, tg, 0.4 * prog(t, 0, 0.6))
    chrome(img, tg)
    text_a(img, (80, 330), "THE 5-YEAR JUMP", dfont("Black", 90), WHITE, clamp(t / 0.3))
    text_a(img, (80, 440), typed("> warheads added, 2021 → 2026", prog(t, 0.2, 1.0)), mono(28), HUD, 1)
    for i, (code, name, inc, lab) in enumerate(JUMP):
        st = 0.6 + i * 0.9; a = clamp((t - st) / 0.25); y = 540 + i * 245
        rect_a(img, (60, y - 10, W - 60, y + 200), (14, 22, 24), a * 0.7, 18, RED if i == 0 else None, 2)
        paste_a(img, flag(code, 130), (90, y + 20), a)
        text_a(img, (250, y + 20), name, font("SemiBold", 44), WHITE, a)
        bw = int(560 * inc / 270 * prog(t, st, 1.2)) + 8
        rect_a(img, (250, y + 100, 250 + bw, y + 150), RED if i == 0 else AMBER, a, 8)
        text_a(img, (W - 90, y + 125), lab, dfont("Black", 64), RED if i == 0 else WHITE, a, "rm")
    text_a(img, (80, 1560), "The other three combined: about +55", font("SemiBold", 44), AMBER, clamp((t - 5.0) / 0.4))

def s_outro(img, t, D, tg):
    radar(img, W / 2, 1050, 520, tg, 0.45 * prog(t, 0, 0.6))
    chrome(img, tg)
    text_a(img, (80, 380), typed("> SHARE OF MILITARY STOCKPILES", prog(t, 0, 0.8)), mono(32), HUD, 1)
    a = clamp((t - 0.4) / 0.3)
    paste_a(img, flag("US", 170), (80, 470), a); paste_a(img, flag("RU", 170), (270, 470), a)
    v = 83 * prog(t, 0.5, 1.6)
    text_a(img, (480, 455), f"{int(v)}%", dfont("Black", 190), RED, a)
    text_a(img, (80, 680), "still held by the USA and Russia", font("SemiBold", 46), WHITE, clamp((t - 1.0) / 0.4))
    text_a(img, (80, 900), typed("But the fastest growth", prog(t, 3.2, 1.0)), dfont("Bold", 72), WHITE, 1)
    text_a(img, (80, 990), typed("is now in Asia.", prog(t, 4.2, 0.8)), dfont("Bold", 72), AMBER, 1)
    for i, c in enumerate(["CN", "IN", "KP", "PK"]):
        st = 5.0 + i * 0.15; paste_a(img, flag(c, 120), (80 + i * 140, 1110 + (1 - back((t - st) / 0.45)) * 50), clamp((t - st) / 0.25))
    p = back((t - 7.6) / 0.5)
    rect_a(img, (80, 1330, 80 + int(560 * clamp(p, 0, 1.2)), 1430), RED, clamp((t - 7.6) / 0.2), 50)
    text_a(img, (110, 1380), "FOLLOW FOR MORE  →", font("Bold", 44), WHITE, clamp((t - 7.9) / 0.3), "lm")

FNS = [("00_title", s_title), ("01_global", s_global)] + [(f"{i+2:02d}_{C[i][0]}", country_scene(i)) for i in range(len(C))] + [("07_jump", s_jump), ("08_outro", s_outro)]
