import os, sys, math, random
sys.path.insert(0, os.path.dirname(__file__))
from artlib import *

OUT = sys.argv[1]  # path to <mod>/graphics
VIOLET = (170, 80, 255)
VIOLET_D = (80, 28, 150)
OUTLINE = (24, 20, 30)

TIERS = {
    1: dict(body=(176, 112, 78), body_d=(104, 62, 44), metal=(78, 72, 80), trim=(214, 160, 96), accent=(255, 150, 60), lamp=(255, 170, 60)),
    2: dict(body=(120, 138, 168), body_d=(64, 76, 102), metal=(44, 52, 70), trim=(176, 198, 226), accent=(110, 205, 255), lamp=(110, 255, 200)),
    3: dict(body=(214, 218, 236), body_d=(122, 128, 166), metal=(58, 62, 92), trim=(255, 255, 255), accent=(255, 110, 250), lamp=(255, 120, 255)),
}
TIER_OF = {
    "antimatter-wellhead": 1, "antimatter-wellhead-2": 2, "antimatter-wellhead-3": 3,
    "matter-converter-burner": 1, "matter-converter": 2, "matter-converter-2": 3,
    "matter-caster-burner": 1, "matter-caster": 2, "matter-caster-2": 3,
}


def save_set(canvas, rel, w, h):
    """write normal + hr-version of a canvas whose logical size is w x h"""
    folder, name = os.path.split(rel)
    os.makedirs(os.path.join(OUT, folder), exist_ok=True)
    canvas.final(1).save(os.path.join(OUT, folder, name))
    canvas.final(2).save(os.path.join(OUT, folder, "hr-" + name))


# ---------------------------------------------------------------- shared pieces
def rivets(c, pts, col=(40, 36, 44)):
    for x, y in pts:
        c.ellipse((x - 1.1, y - 1.1, x + 1.1, y + 1.1), fill=shade(col, 0.8))
        c.ellipse((x - 0.9, y - 1.0, x + 0.3, y + 0.1), fill=shade(col, 1.9))


def smoke(c, x, y):
    rnd = random.Random(int(x * 7 + y))
    for i in range(5):
        r = 3 + i * 1.4
        xx = x + rnd.uniform(-2, 2) + i * 1.2
        yy = y - i * 6
        a = int(120 - i * 20)
        c.ellipse((xx - r, yy - r, xx + r, yy + r), fill=(205, 205, 210, max(20, a)))


def chimney(c, x, y_top, y_base, pal, w=9):
    c.grad((x, y_top, x + w, y_base), shade(pal["body"], 0.95), shade(pal["body_d"], 0.8), horizontal=True)
    c.rect((x - 1.2, y_top - 2.5, x + w + 1.2, y_top + 0.8), fill=shade(pal["metal"], 1.0), outline=OUTLINE, width=0.6)
    c.ellipse((x + 1, y_top - 1.8, x + w - 1, y_top + 0.4), fill=(20, 16, 20))
    for yy in range(int(y_top + 5), int(y_base) - 2, 5):
        c.line([(x, yy), (x + w, yy)], shade(pal["body_d"], 0.6), 0.6)
    smoke(c, x + w / 2, y_top - 3)


def pipe_nub(c, side, x, y, col, ring):
    """short pipe stub at a connection; side tells where the machine edge is."""
    dark = shade(col, 0.55)
    if side == "N":
        c.grad((x - 4.5, y - 9, x + 4.5, y + 1), shade(col, 1.25), dark, horizontal=True)
        c.rect((x - 5.5, y - 10.5, x + 5.5, y - 7.5), fill=shade(col, 0.9), outline=OUTLINE, width=0.6)
        c.rect((x - 3.8, y - 9.8, x + 3.8, y - 8.2), fill=ring)
    elif side == "E":
        c.grad((x - 1, y - 4.5, x + 9, y + 4.5), shade(col, 1.25), dark)
        c.rect((x + 7.5, y - 5.5, x + 10.5, y + 5.5), fill=shade(col, 0.9), outline=OUTLINE, width=0.6)
        c.rect((x + 8.2, y - 3.8, x + 9.8, y + 3.8), fill=ring)
    elif side == "W":
        c.grad((x - 9, y - 4.5, x + 1, y + 4.5), shade(col, 1.25), dark)
        c.rect((x - 10.5, y - 5.5, x - 7.5, y + 5.5), fill=shade(col, 0.9), outline=OUTLINE, width=0.6)
        c.rect((x - 9.8, y - 3.8, x - 8.2, y + 3.8), fill=ring)
    else:  # S: round port on the front face
        c.ellipse((x - 6, y - 6, x + 6, y + 6), fill=shade(col, 0.7), outline=OUTLINE, width=0.7)
        c.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(18, 14, 20))
        c.ellipse((x - 4, y - 4, x + 4, y + 4), outline=ring, width=1.1)


def rot(p, d):
    x, y = p
    return {"north": (x, y), "east": (-y, x), "south": (-x, -y), "west": (y, -x)}[d]


def side_off(p):
    x, y = p
    if abs(y) > abs(x):
        return ("N" if y < 0 else "S", x * 32)
    return ("E" if x > 0 else "W", y * 32)


def box_machine(c, foot, hh, pal, glow_col):
    """front face + top face of a box standing on `foot` (ground rectangle)."""
    x0, y0, x1, y1 = foot
    ty0, ty1 = y0 - hh, y1 - hh
    # contact shadow
    c.blur_layer(lambda t: t.rrect((x0 + 1, y1 - 4, x1 + 1, y1 + 2), 3, fill=(0, 0, 0, 170)), 1.6)
    # front face
    c.grad((x0, ty1 - 6, x1, y1), shade(pal["body"], 0.85), shade(pal["body_d"], 0.55), shape="rrect", r=3.5)
    c.rrect((x0, ty1 - 6, x1, y1), 3.5, outline=OUTLINE, width=0.9)
    c.line([(x0 + 2, ty1 + 4), (x1 - 2, ty1 + 4)], shade(pal["body_d"], 0.45), 0.7)
    c.line([(x0 + 2, ty1 + 4.8), (x1 - 2, ty1 + 4.8)], shade(pal["body"], 1.25), 0.5)
    rivets(c, [(x0 + 4, y1 - 5), (x1 - 4, y1 - 5), (x0 + 4, ty1 + 9), (x1 - 4, ty1 + 9)])
    # top face
    c.grad((x0, ty0, x1, ty1), shade(pal["body"], 1.28), shade(pal["body"], 0.95), shape="rrect", r=5)
    c.rrect((x0, ty0, x1, ty1), 5, outline=OUTLINE, width=1.0)
    c.rrect((x0 + 1.6, ty0 + 1.6, x1 - 1.6, ty1 - 1.6), 4, outline=shade(pal["trim"], 1.0) + (110,), width=0.7)
    c.noise((x0, ty0, x1, y1), 7, seed=int(x0 + y0))
    rivets(c, [(x0 + 4.5, ty0 + 4.5), (x1 - 4.5, ty0 + 4.5), (x0 + 4.5, ty1 - 4.5), (x1 - 4.5, ty1 - 4.5)])
    return ty0, ty1


def lamps(c, x, y, pal, n=3, gap=5.5):
    for i in range(n):
        cx = x + i * gap
        c.glow(cx, y, 4.5, pal["lamp"], 0.55)
        c.ellipse((cx - 1.6, y - 1.6, cx + 1.6, y + 1.6), fill=shade(pal["lamp"], 1.2), outline=OUTLINE, width=0.4)


def firebox(c, x, y_top, y_bot, pal):
    """arched fuel door on a front face for the burner tier."""
    w = 14
    c.rrect((x, y_top, x + w, y_bot), 3, fill=(24, 18, 20), outline=OUTLINE, width=0.8)
    c.glow(x + w / 2, (y_top + y_bot) / 2 + 1, 9, (255, 120, 30), 0.95)
    c.rrect((x + 2, y_top + 3, x + w - 2, y_bot - 1.5), 2, fill=(255, 150, 40))
    c.rrect((x + 3.6, y_top + 5.5, x + w - 3.6, y_bot - 1.5), 1.6, fill=(255, 224, 120))
    c.line([(x + 1, y_top + 2), (x + w - 1, y_top + 2)], shade(pal["metal"], 1.5), 0.9)


# ---------------------------------------------------------------- wellhead
def draw_wellhead(tier):
    pal = TIERS[tier]
    c = Canvas(128, 144)
    ty0, ty1 = box_machine(c, (16, 48, 112, 144), 12, pal, VIOLET)
    cx, cy = 64, 86
    # bore housing (cylinder)
    c.blur_layer(lambda t: t.ellipse((38, cy - 2, 92, cy + 20), fill=(0, 0, 0, 150)), 1.5)
    c.ellipse((40, 80, 88, 106), fill=shade(pal["metal"], 0.8), outline=OUTLINE, width=0.8)
    c.grad((40, 62, 88, 93), shade(pal["body_d"], 0.7), shade(pal["body_d"], 0.7), horizontal=True)
    # shaded cylinder body: dark-light-dark
    c.grad((40, 62, 64, 93), shade(pal["body_d"], 0.65), shade(pal["body"], 1.05), horizontal=True)
    c.grad((64, 62, 88, 93), shade(pal["body"], 1.05), shade(pal["body_d"], 0.55), horizontal=True)
    c.line([(40, 62), (40, 93)], OUTLINE, 0.9)
    c.line([(88, 62), (88, 93)], OUTLINE, 0.9)
    c.ellipse((40, 80, 88, 106), outline=OUTLINE, width=0.0)
    # lower rim of cylinder painted over body bottom
    c.d.pieslice(c._s((40, 80, 88, 106)), 0, 180, fill=None, outline=OUTLINE, width=int(0.9 * R))
    for yy in (70, 78, 86):
        c.line([(41, yy + 1.5), (64, yy + 5), (87, yy + 1.5)], shade(pal["body_d"], 0.5), 0.8)
    # top of the housing
    c.ellipse((40, 48, 88, 76), fill=shade(pal["trim"], 0.95), outline=OUTLINE, width=0.9)
    c.ellipse((46, 53, 82, 71), fill=(22, 12, 34), outline=shade(pal["metal"], 1.2), width=1.2)
    c.glow(64, 62, 17, VIOLET, 0.9)
    c.ellipse((52, 57, 76, 67), fill=VIOLET_D)
    c.glow(64, 62, 9, (225, 180, 255), 0.95)
    # tower lattice
    for sgn in (-1, 1):
        c.poly([(64 + sgn * 9, 62), (64 + sgn * 4, 20), (64 + sgn * 6.5, 20), (64 + sgn * 12, 62)], fill=shade(pal["metal"], 1.1), outline=OUTLINE)
    for i, yy in enumerate(range(26, 60, 8)):
        w1 = 4 + (yy - 20) * 0.19
        w2 = 4 + (yy + 8 - 20) * 0.19
        c.line([(64 - w1, yy), (64 + w2, yy + 8)], shade(pal["metal"], 1.5), 0.9)
        c.line([(64 + w1, yy), (64 - w2, yy + 8)], shade(pal["metal"], 1.5), 0.9)
    # antimatter conduit
    c.glow(64, 40, 12, VIOLET, 0.55)
    c.rect((61.5, 20, 66.5, 62), fill=(210, 150, 255), outline=VIOLET_D, width=0.8)
    c.rect((63, 20, 65, 62), fill=(250, 235, 255))
    # head
    c.glow(64, 16, 17, VIOLET, 1.0)
    c.ellipse((56, 8, 72, 24), fill=shade(pal["trim"], 0.9), outline=OUTLINE, width=0.9)
    c.ellipse((58.5, 10.5, 69.5, 21.5), fill=(236, 205, 255))
    c.glow(64, 16, 8, (255, 255, 255), 1.0)

    if tier == 1:
        # wood-fired firebox with a chimney on the right, logs on the left
        c.grad((88, 74, 112, 112), shade(pal["body"], 1.05), shade(pal["body_d"], 0.8), shape="rrect", r=2.5)
        c.rrect((88, 74, 112, 112), 2.5, outline=OUTLINE, width=0.9)
        for yy in range(78, 110, 7):
            c.line([(89, yy), (111, yy)], shade(pal["body_d"], 0.55), 0.6)
        firebox(c, 93, 90, 108, pal)
        chimney(c, 99, 28, 78, pal)
        c.line([(75, 97), (92, 97)], shade(pal["metal"], 1.4), 2.2)  # feed pipe to the head
        for i, (lx, ly) in enumerate([(22, 108), (22, 118), (30, 113)]):
            c.rect((lx, ly - 3.2, lx + 20, ly + 3.2), fill=(122, 80, 48), outline=(52, 32, 20), width=0.7)
            c.ellipse((lx - 3, ly - 3.2, lx + 3, ly + 3.2), fill=(216, 170, 110), outline=(52, 32, 20), width=0.7)
            c.ellipse((lx - 1.2, ly - 1.4, lx + 1.2, ly + 1.4), outline=(150, 100, 60), width=0.5)
    elif tier == 2:
        for yy, r in ((36, 10), (46, 11)):
            c.ellipse((64 - r, yy - 3.5, 64 + r, yy + 3.5), outline=(230, 150, 90), width=1.5)
            c.ellipse((64 - r + 1, yy - 2.5, 64 + r - 1, yy + 2.5), outline=(110, 205, 255, 200), width=0.7)
        c.grad((88, 84, 110, 110), shade(pal["body"], 1.15), shade(pal["body_d"], 0.8), shape="rrect", r=2.5)
        c.rrect((88, 84, 110, 110), 2.5, outline=OUTLINE, width=0.9)
        lamps(c, 93, 90, pal, 3, 5.5)
        c.rect((92, 98, 106, 104), fill=(26, 30, 44), outline=OUTLINE, width=0.5)
        c.line([(75, 100), (88, 100)], (230, 150, 90), 1.6)
        c.line([(22, 112), (36, 106), (46, 100)], (50, 50, 60), 2.2)
        c.ellipse((18, 108, 30, 120), fill=shade(pal["body"], 1.1), outline=OUTLINE, width=0.8)
        c.ellipse((20, 110, 28, 118), fill=(26, 30, 44))
        c.glow(24, 114, 7, pal["accent"], 0.7)
    else:
        for yy, r, a in ((26, 15, 255), (34, 19, 220), (44, 24, 190)):
            c.glow(64, yy, r + 4, pal["accent"], 0.18)
            c.ellipse((64 - r, yy - 4.5, 64 + r, yy + 4.5), outline=pal["accent"] + (a,), width=1.7)
            c.ellipse((64 - r + 2, yy - 3.2, 64 + r - 2, yy + 3.2), outline=(255, 235, 255, int(a * 0.5)), width=0.6)
        c.grad((86, 80, 110, 112), shade(pal["body"], 1.1), shade(pal["body_d"], 0.8), shape="rrect", r=2.5)
        c.rrect((86, 80, 110, 112), 2.5, outline=OUTLINE, width=0.9)
        lamps(c, 91, 86, pal, 4, 4.8)
        c.glow(98, 100, 8, pal["accent"], 0.7)
        c.ellipse((92, 94, 104, 106), fill=(30, 20, 56), outline=OUTLINE, width=0.6)
        c.ellipse((95, 97, 101, 103), fill=pal["accent"])
        c.rect((20, 92, 36, 118), fill=shade(pal["metal"], 1.1), outline=OUTLINE, width=0.8)
        c.glow(28, 105, 9, VIOLET, 0.8)
        c.rect((24, 96, 32, 114), fill=(200, 140, 255), outline=VIOLET_D, width=0.6)
        c.line([(76, 100), (86, 100)], pal["accent"], 1.8)
        c.line([(36, 104), (64, 104)], pal["accent"] + (200,), 1.6)
    return c


# ---------------------------------------------------------------- converter 2x3
CONV_IN = [(-0.5, -2), (0.5, -2)]
CONV_OUT = [(-0.5, 2), (0.5, 2)]


def draw_converter(tier, d):
    pal = TIERS[tier]
    if d in ("north", "south"):
        c = Canvas(96, 144); foot = (16, 48, 80, 144)
    else:
        c = Canvas(144, 112); foot = (24, 48, 120, 112)
    hh = 30
    x0, y0, x1, y1 = foot
    cx = (x0 + x1) / 2
    ty0, ty1 = box_machine(c, foot, hh, pal, VIOLET)
    tcy = (ty0 + ty1) / 2
    # chimney for the burner tier (drawn before the dome so the dome overlaps its foot)
    if tier == 1:
        if d in ("north", "south"):
            chimney(c, x1 - 12, ty0 - 12, ty0 + 12, pal, w=8)
        else:
            chimney(c, x0 + 6, ty0 - 12, ty0 + 12, pal, w=8)
    # reaction dome
    r = 11 if d in ("north", "south") else 11
    c.glow(cx, tcy, r + 8, VIOLET, 0.55)
    c.ellipse((cx - r - 3, tcy - r - 3, cx + r + 3, tcy + r + 3), fill=shade(pal["trim"], 0.9), outline=OUTLINE, width=0.9)
    c.ellipse((cx - r, tcy - r, cx + r, tcy + r), fill=(20, 10, 34), outline=shade(pal["metal"], 1.3), width=1.0)
    c.glow(cx, tcy, r, VIOLET, 1.0)
    c.ellipse((cx - r * 0.55, tcy - r * 0.55, cx + r * 0.55, tcy + r * 0.55), fill=(225, 180, 255))
    c.glow(cx, tcy, r * 0.5, (255, 255, 255), 1.0)
    c.d.arc(c._s((cx - r + 1.5, tcy - r + 1.5, cx + r - 1.5, tcy + r - 1.5)), 200, 290, fill=(255, 255, 255, 200), width=int(1.0 * R))
    # vent slits on the top face
    if d in ("north", "south"):
        for k in (-1, 1):
            for j in range(3):
                c.rect((cx - 12, tcy + k * 27 - 3 + j * 3.2 - 3, cx + 12, tcy + k * 27 - 2 + j * 3.2 - 3), fill=shade(pal["metal"], 0.7))
    else:
        for k in (-1, 1):
            for j in range(3):
                c.rect((cx + k * 34 - 6 + j * 3.2, tcy - 8, cx + k * 34 - 5 + j * 3.2, tcy + 8), fill=shade(pal["metal"], 0.7))
    # front face: lamps + (burner) firebox
    fy = (ty1 + y1) / 2
    if tier == 1 and d in ("east", "west"):
        firebox(c, x0 + 7, ty1 + 5, y1 - 3, pal)
        lamps(c, x1 - 18, fy + 2, pal, 3, 5)
    elif d in ("east", "west"):
        lamps(c, cx - 5.5, fy + 1, pal, 3, 5.5)
    else:  # ports sit on the front face (south) or the face is plain (north)
        lamps(c, cx - 5.5, ty1 + 8, pal, 3, 5.5) if d == "south" else lamps(c, cx - 5.5, fy + 1, pal, 3, 5.5)
    # pipe connections
    for p in CONV_IN:
        side, off = side_off(rot(p, d))
        px, py = {"N": (cx + off, ty0), "S": (cx + off, fy), "E": (x1, tcy + off), "W": (x0, tcy + off)}[side]
        pipe_nub(c, side, px, py, (118, 92, 168), (190, 120, 255))
    for p in CONV_OUT:
        side, off = side_off(rot(p, d))
        px, py = {"N": (cx + off, ty0), "S": (cx + off, fy), "E": (x1, tcy + off), "W": (x0, tcy + off)}[side]
        pipe_nub(c, side, px, py, (110, 108, 116), (255, 170, 80))
    return c


# ---------------------------------------------------------------- caster 3x3
def draw_caster(tier, d):
    pal = TIERS[tier]
    c = Canvas(128, 144)
    hh = 34
    foot = (16, 48, 112, 144)
    x0, y0, x1, y1 = foot
    cx = 64
    ty0, ty1 = box_machine(c, foot, hh, pal, (255, 140, 40))
    tcy = (ty0 + ty1) / 2
    if tier == 1:
        chimney(c, cx - 5, ty0 - 12, ty0 + 14, pal, w=10)
    # crucible
    r = 27
    c.glow(cx, tcy + 2, r + 12, (255, 120, 30), 0.5)
    c.ellipse((cx - r - 4, tcy - r - 3 + 2, cx + r + 4, tcy + r + 3 + 2), fill=shade(pal["trim"], 0.85), outline=OUTLINE, width=1.0)
    c.ellipse((cx - r, tcy - r + 2, cx + r, tcy + r + 2), fill=(30, 18, 16), outline=shade(pal["metal"], 1.2), width=1.2)
    c.grad((cx - r + 3, tcy - r + 5, cx + r - 3, tcy + r - 1), (255, 220, 120), (255, 90, 20), shape="ellipse")
    c.glow(cx, tcy + 2, r - 4, (255, 200, 90), 0.8)
    rnd = random.Random(tier * 11 + 3)
    for i in range(9):
        a = rnd.uniform(0, 6.28); rr = rnd.uniform(0, r - 8)
        bx, by = cx + math.cos(a) * rr, tcy + 2 + math.sin(a) * rr * 0.95
        c.ellipse((bx - 1.6, by - 1.2, bx + 1.6, by + 1.2), fill=(255, 245, 190))
    c.d.arc(c._s((cx - r + 2, tcy - r + 4, cx + r - 2, tcy + r)), 200, 300, fill=(255, 255, 255, 180), width=int(1.1 * R))
    # spout to the front tray
    c.poly([(cx - 8, tcy + r - 2), (cx + 8, tcy + r - 2), (cx + 5, tcy + r + 6), (cx - 5, tcy + r + 6)], fill=shade(pal["metal"], 1.1), outline=OUTLINE)
    c.rect((cx - 2.5, tcy + r + 1, cx + 2.5, tcy + r + 6), fill=(255, 180, 70))
    # front face: tray, firebox, lamps
    fy = (ty1 + y1) / 2
    c.rrect((cx - 12, ty1 + 6, cx + 12, y1 - 5), 2.5, fill=(22, 16, 18), outline=OUTLINE, width=0.8)
    c.glow(cx, ty1 + 8, 8, (255, 140, 40), 0.7)
    c.rrect((cx - 9, ty1 + 6, cx + 9, ty1 + 10), 1.5, fill=(255, 150, 50))
    if tier == 1 and d != "south":
        firebox(c, x0 + 8, ty1 + 4, y1 - 4, pal)
        lamps(c, x1 - 22, fy, pal, 3, 5.5)
    elif tier == 1:
        lamps(c, cx - 5.5, ty1 + 6, pal, 3, 5.5)
    else:
        lamps(c, x0 + 10, fy, pal, 3, 5.5)
        lamps(c, x1 - 22, fy, pal, 3, 5.5)
    # molten inlets (two on the input side)
    for p in [(-1, -2), (1, -2)]:
        side, off = side_off(rot(p, d))
        px, py = {"N": (cx + off, ty0), "S": (cx + off, fy), "E": (x1, tcy + off), "W": (x0, tcy + off)}[side]
        pipe_nub(c, side, px, py, (150, 96, 74), (255, 150, 60))
    return c


# ---------------------------------------------------------------- isotope separator 3x3
def draw_separator(d):
    pal = dict(body=(120, 160, 138), body_d=(54, 86, 70), metal=(40, 58, 52), trim=(190, 232, 206), accent=(120, 255, 150), lamp=(120, 255, 150))
    c = Canvas(128, 144)
    hh = 36
    foot = (16, 48, 112, 144)
    x0, y0, x1, y1 = foot
    cx = 64
    ty0, ty1 = box_machine(c, foot, hh, pal, (120, 255, 150))
    tcy = (ty0 + ty1) / 2
    G = (110, 255, 150)
    r = 30
    c.glow(cx, tcy, r + 10, G, 0.5)
    c.ellipse((cx - r - 3, tcy - r - 3, cx + r + 3, tcy + r + 3), fill=shade(pal["trim"], 0.85), outline=OUTLINE, width=1.0)
    c.ellipse((cx - r, tcy - r, cx + r, tcy + r), fill=(12, 26, 20), outline=shade(pal["metal"], 1.4), width=1.2)
    for k, rr in enumerate((24, 17, 10)):
        c.ellipse((cx - rr, tcy - rr, cx + rr, tcy + rr), outline=G + (255 - k * 40,), width=1.8)
        n = 8 - k * 2
        for i in range(n):
            a = i * 2 * math.pi / n + k * 0.4
            c.line([(cx + math.cos(a) * (rr - 5), tcy + math.sin(a) * (rr - 5)), (cx + math.cos(a) * rr, tcy + math.sin(a) * rr)], (210, 255, 225), 1.2)
    c.glow(cx, tcy, 14, G, 1.0)
    c.ellipse((cx - 5, tcy - 5, cx + 5, tcy + 5), fill=(235, 255, 240), outline=OUTLINE, width=0.6)
    c.glow(cx, tcy, 6, (255, 255, 255), 1.0)
    # hazard stripes on the corners
    for sx in (x0 + 5, x1 - 17):
        for i in range(3):
            c.poly([(sx + i * 4, ty1 - 5), (sx + i * 4 + 2.5, ty1 - 5), (sx + i * 4 + 5.5, ty1 - 1.5), (sx + i * 4 + 3, ty1 - 1.5)], fill=(255, 210, 40))
    fy = (ty1 + y1) / 2
    lamps(c, x0 + 10, fy, pal, 3, 5.5)
    lamps(c, x1 - 22, fy, pal, 3, 5.5)
    c.rrect((cx - 10, ty1 + 6, cx + 10, y1 - 6), 2.5, fill=(14, 22, 18), outline=OUTLINE, width=0.8)
    c.glow(cx, fy, 8, G, 0.6)
    side, off = side_off(rot((-1, -2), d))
    px, py = {"N": (cx + off, ty0), "S": (cx + off, fy), "E": (x1, tcy + off), "W": (x0, tcy + off)}[side]
    pipe_nub(c, side, px, py, (118, 92, 168), (190, 120, 255))
    return c


# ---------------------------------------------------------------- ground well (resource)
def draw_well():
    c = Canvas(96, 96)
    rnd = random.Random(7)
    c.blur_layer(lambda t: t.ellipse((4, 22, 92, 88), fill=(0, 0, 0, 130)), 2)
    c.grad((6, 16, 90, 84), (112, 96, 104), (54, 44, 58), shape="ellipse")
    c.ellipse((6, 16, 90, 84), outline=OUTLINE, width=1.2)
    for i in range(46):
        a = rnd.uniform(0, 6.283)
        rx, ry = 40 + rnd.uniform(-4, 3), 33 + rnd.uniform(-3, 3)
        x, y = 48 + math.cos(a) * rx, 50 + math.sin(a) * ry
        s = rnd.uniform(2, 5.2)
        sh = rnd.uniform(0.65, 1.3)
        c.poly([(x - s, y), (x - s * 0.3, y - s * 0.9), (x + s * 0.8, y - s * 0.5), (x + s, y + s * 0.4), (x, y + s * 0.8)],
               fill=shade((128, 112, 122), sh), outline=(34, 28, 38))
    c.ellipse((14, 24, 82, 76), fill=(14, 6, 26), outline=(40, 18, 70), width=1.4)
    c.glow(48, 50, 30, VIOLET, 0.95)
    for k in range(3):
        pts = []
        for t in range(0, 60):
            a = t * 0.19 + k * 2.09
            rr = 3 + t * 0.52
            pts.append((48 + math.cos(a) * rr * 1.0, 50 + math.sin(a) * rr * 0.78))
        c.line(pts, (210, 160, 255, 230), 1.4)
    c.glow(48, 50, 15, (230, 190, 255), 1.0)
    c.glow(48, 50, 7, (255, 255, 255), 1.0)
    for i in range(14):
        a = rnd.uniform(0, 6.283); rr = rnd.uniform(6, 28)
        x, y = 48 + math.cos(a) * rr, 50 + math.sin(a) * rr * 0.78
        c.glow(x, y, 3, (240, 210, 255), 1.0)
    return c


# ---------------------------------------------------------------- icons
def teardrop_pts(cx=32, tip=5, cy=40, r=20, n=40):
    d = cy - tip
    th = math.acos(r / d)
    pts = [(cx, tip)]
    # right tangent point, around the bottom, left tangent point
    a0 = th
    a1 = 2 * math.pi - th
    for k in range(n + 1):
        a = a0 + (a1 - a0) * k / n
        pts.append((cx + r * math.sin(a), cy - r * math.cos(a)))
    return pts


def droplet(base, mid, hi, glowc, core=None):
    c = Canvas(64, 64)
    pts = teardrop_pts()
    c.glow(32, 40, 31, glowc, 0.5)
    c.grad((10, 5, 54, 61), hi, base, shape="poly", pts=pts)
    c.grad((10, 22, 54, 61), mid + (0,), shade(base, 0.8) + (255,), shape="poly", pts=pts)
    c.poly(pts, outline=OUTLINE)
    c.line(pts + [pts[0]], OUTLINE, 1.6)
    if core:
        c.glow(32, 42, 11, core, 1.0)
    c.glow(30, 38, 12, shade(hi, 1.25), 0.45)
    c.ellipse((21, 33, 28, 46), fill=(255, 255, 255, 170))
    c.ellipse((22.5, 35, 25.5, 40), fill=(255, 255, 255, 255))
    c.ellipse((38, 50, 43, 54), fill=(255, 255, 255, 110))
    return c


def icon_fluid(name):
    spec = {
        "antimatter-fluid": ((70, 18, 150), (150, 70, 235), (222, 170, 255), (180, 90, 255), (255, 240, 255)),
        "molten-iron": ((190, 60, 10), (255, 130, 30), (255, 226, 130), (255, 130, 30), None),
        "molten-copper": ((150, 54, 22), (224, 110, 56), (255, 190, 130), (255, 110, 50), None),
        "molten-stone": ((90, 20, 10), (200, 70, 30), (255, 150, 80), (255, 90, 30), None),
        "liquid-carbon": ((10, 10, 16), (40, 42, 58), (110, 120, 150), (90, 100, 140), None),
    }[name]
    return droplet(*spec)


def icon_from_sprite(canvas, ):
    return fit_icon(canvas.final(2), 64, 3)


def icon_well():
    c = draw_well()
    return fit_icon(c.final(2), 64, 3)


def tech_icon(level):
    c = Canvas(256, 256)
    c.glow(128, 128, 126, (60, 24, 120), 1.0, power=1.2)
    c.ellipse((10, 10, 246, 246), outline=(150, 90, 230), width=3)
    c.ellipse((18, 18, 238, 238), outline=(70, 36, 130), width=2)
    rnd = random.Random(level)
    for i in range(46):
        a = rnd.uniform(0, 6.283); rr = rnd.uniform(40, 112)
        c.glow(128 + math.cos(a) * rr, 128 + math.sin(a) * rr, rnd.uniform(1.5, 3.5), (230, 200, 255), 1.0)
    # orbits
    for k in range(level + 1):
        c.d.arc(c._s((28 + k * 6, 60 + k * 14, 228 - k * 6, 196 - k * 14)), 200 + k * 25, 340 + k * 25, fill=(210, 150, 255, 230), width=int(2 * R))
    wh = draw_wellhead(level + 1)
    spr = wh.final(2)
    s = 190 / spr.size[1]
    spr = spr.convert("RGBa").resize((int(spr.size[0] * s), int(spr.size[1] * s)), Image.LANCZOS).convert("RGBA")
    c.img.alpha_composite(spr.resize((spr.size[0] * R, spr.size[1] * R), Image.LANCZOS), (int((256 - spr.size[0]) / 2 * R), int(40 * R)))
    if level == 1:
        c.poly([(196, 150), (170, 190), (186, 190), (174, 232), (216, 178), (198, 178), (212, 150)], fill=(255, 235, 120), outline=(120, 80, 10))
        c.glow(194, 190, 26, (255, 230, 120), 0.7)
    else:
        c.glow(128, 40, 30, (255, 120, 250), 0.8)
        c.glow(128, 40, 12, (255, 255, 255), 1.0)
    return c


def save_icon(img, rel):
    os.makedirs(os.path.join(OUT, os.path.dirname(rel)), exist_ok=True)
    img.save(os.path.join(OUT, rel))


if __name__ == "__main__":
    # entities
    for name, tier in (("antimatter-wellhead", 1), ("antimatter-wellhead-2", 2), ("antimatter-wellhead-3", 3)):
        c = draw_wellhead(tier)
        save_set(c, f"entity/antimatter-wellhead/{name}.png", 128, 144)
        save_icon(fit_icon(c.final(2), 64, 3), f"icons/{name}.png")
    for name in ("matter-converter-burner", "matter-converter", "matter-converter-2"):
        tier = TIER_OF[name]
        for d in ("north", "east", "south", "west"):
            c = draw_converter(tier, d)
            save_set(c, f"entity/matter-converter/{name}-{d}.png", c.w, c.h)
            if d == "north":
                save_icon(fit_icon(c.final(2), 64, 3), f"icons/{name}.png")
    for name in ("matter-caster-burner", "matter-caster", "matter-caster-2"):
        tier = TIER_OF[name]
        for d in ("north", "east", "south", "west"):
            c = draw_caster(tier, d)
            save_set(c, f"entity/matter-caster/{name}-{d}.png", 128, 144)
            if d == "north":
                save_icon(fit_icon(c.final(2), 64, 3), f"icons/{name}.png")
    for d in ("north", "east", "south", "west"):
        c = draw_separator(d)
        save_set(c, f"entity/isotope-separator/isotope-separator-{d}.png", 128, 144)
        if d == "north":
            save_icon(fit_icon(c.final(2), 64, 3), "icons/isotope-separator.png")
    c = draw_well()
    save_set(c, "entity/antimatter-well/antimatter-well.png", 96, 96)
    save_icon(fit_icon(c.final(2), 64, 3), "icons/antimatter-well.png")
    for f in ("antimatter-fluid", "molten-iron", "molten-copper", "molten-stone", "liquid-carbon"):
        save_icon(icon_fluid(f).final(1), f"icons/{f}.png")
    save_icon(tech_icon(1).final(1), "technology/antimatter-electric.png")
    save_icon(tech_icon(2).final(1), "technology/antimatter-advanced.png")
    print("done")
