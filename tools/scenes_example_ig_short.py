# Example: compact Instagram edit scenes for reel 002 (paste into a copy of render_template.py)
ROWS1 = [("CN", "CHINA", "350", 350, 620, "~620"), ("IN", "INDIA", "156", 156, 190, "~190")]
ROWS2 = [("KP", "NORTH KOREA", "40–50", 45, 60, "~60"), ("PK", "PAKISTAN", "165", 165, 170, "~170"), ("GB", "UK", "cap 180", 180, 260, "cap 260")]

def rows_scene(rows, head, sub):
    def s(img, t, D, tg):
        radar(img, W - 60, 1100, 460, tg, 0.4 * prog(t, 0, 0.6))
        chrome(img, tg)
        text_a(img, (80, 330), head, dfont("Black", 84), WHITE, clamp(t / 0.3))
        text_a(img, (80, 440), typed(sub, prog(t, 0.2, 0.8)), mono(28), HUD, 1)
        n = len(rows); gap = 300 if n == 2 else 250
        for i, (code, name, l0, v0, v1, lbl) in enumerate(rows):
            st = 0.3 + i * (D - 1.2) / n
            a = clamp((t - st) / 0.25); dx = (1 - back((t - st) / 0.5)) * 140; y = 540 + i * gap
            rect_a(img, (60, y - 10, W - 60, y + gap - 40), (14, 22, 24), a * 0.75, 18, RED if i == 0 else None, 2)
            paste_a(img, flag(code, 150), (90 + dx, y + 20), a)
            text_a(img, (270 + dx, y + 20), name, font("SemiBold", 46), WHITE, a)
            g = prog(t, st + 0.2, 1.0)
            cur = lbl if g >= 0.999 else (("cap " if lbl.startswith("cap") else "~") + str(int(round(v0 + (v1 - v0) * g))))
            text_a(img, (270 + dx, y + 85), f"{l0}  →", font("SemiBold", 44), MUTED, a)
            text_a(img, (W - 100, y + 105), cur, dfont("Black", 96), RED if i == 0 else AMBER, a, "rm")
    return s

def s_ig_outro(img, t, D, tg):
    radar(img, W / 2, 1050, 520, tg, 0.45 * prog(t, 0, 0.6))
    chrome(img, tg)
    text_a(img, (80, 420), typed("> FASTEST GROWTH", prog(t, 0, 0.6)), mono(34), HUD, 1)
    text_a(img, (80, 480), "IS NOW IN ASIA", dfont("Black", 104), AMBER, clamp((t - 0.4) / 0.3))
    for i, c in enumerate(["CN", "IN", "KP", "PK"]):
        st = 0.9 + i * 0.15; paste_a(img, flag(c, 150), (80 + i * 175, 660 + (1 - back((t - st) / 0.45)) * 50), clamp((t - st) / 0.25))
    a = clamp((t - 2.2) / 0.3)
    rect_a(img, (60, 950, W - 60, 1190), (40, 8, 12), a * 0.9, 24, RED, 3)
    text_a(img, (100, 1000), "▶ FULL VIDEO ON YOUTUBE", dfont("Black", 60), WHITE, a)
    text_a(img, (100, 1090), "@Unknown_Uncovered_2026", font("SemiBold", 48), AMBER, a)
    p = back((t - 3.0) / 0.5)
    rect_a(img, (80, 1290, 80 + int(560 * clamp(p, 0, 1.2)), 1390), RED, clamp((t - 3.0) / 0.2), 50)
    text_a(img, (110, 1340), "FOLLOW FOR MORE  →", font("Bold", 44), WHITE, clamp((t - 3.3) / 0.3), "lm")

FNS = [("00_title", s_title), ("01_rows1", rows_scene(ROWS1, "5-YEAR JUMP", "> warheads, 2021 → 2026")),
       ("02_rows2", rows_scene(ROWS2, "ALSO RISING", "> warheads, 2021 → 2026")), ("03_outro", s_ig_outro)]
