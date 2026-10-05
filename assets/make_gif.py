"""Original pixel-art hero GIF: a little PM-bot that waves while its ROI chart climbs."""
from PIL import Image, ImageDraw
import math

U = 8                      # pixel unit
W, H = 76, 30              # canvas in units
FRAMES = 36

# palette (indexed, 0 = transparent)
PAL = {
    "t": (0, 0, 0),         # transparent key
    "H": (79, 70, 229),     # indigo shell
    "h": (55, 48, 163),     # indigo shade
    "F": (224, 231, 255),   # face screen
    "E": (17, 24, 39),      # eyes
    "M": (16, 185, 129),    # mouth (green)
    "A": (250, 204, 21),    # antenna light on
    "a": (148, 163, 184),   # antenna stem / grey
    "B": (99, 102, 241),    # body
    "C": (16, 185, 129),    # chest light
    "S": (203, 213, 225),   # shadow
    "G": (16, 185, 129),    # chart green
    "g": (5, 150, 105),     # chart green shade
    "I": (129, 140, 248),   # chart indigo
    "i": (79, 70, 229),     # chart indigo shade
    "X": (100, 116, 139),   # axis
    "Y": (250, 204, 21),    # sparkle
    "P": (236, 72, 153),    # sparkle pink
}
KEYS = list(PAL)

ROBOT = [
    "......A......",
    "......a......",
    "..hHHHHHHHh..",
    ".hHHHHHHHHHh.",
    ".HFFFFFFFFFH.",
    ".HFFEFFFEFFH.",
    ".HFFEFFFEFFH.",
    ".HFFFFFFFFFH.",
    ".HFFFMMMFFFH.",
    ".hHHHHHHHHHh.",
    "....aaaaa....",
    "...BBBBBBB...",
    "...BBBCBBB...",
    "...BBBBBBB...",
    "....B...B....",
    "....h...h....",
]


def put(px, x, y, key):
    if 0 <= x < W and 0 <= y < H:
        px[y][x] = key


def frame(f):
    px = [["t"] * W for _ in range(H)]
    t = f / FRAMES

    # --- robot -------------------------------------------------------
    bob = 1 if (f // 3) % 2 else 0
    rx, ry = 6, 7 + bob
    blink = f % 18 in (12, 13)
    for y, row in enumerate(ROBOT):
        for x, k in enumerate(row):
            if k == ".":
                continue
            if k == "A" and (f // 4) % 2:
                k = "a"
            if k == "E" and blink:
                k = "F" if y == 5 else "E"
            if k == "C" and (f // 2) % 3 == 0:
                k = "G"
            put(px, rx + x, ry + y, k)
    # left arm (static, down)
    for d in range(3):
        put(px, rx + 2, ry + 11 + d, "B")
    # right arm waves
    wave = (f // 3) % 4
    if wave in (0, 2):     # arm raised
        arm = [(10, 12), (11, 11), (12, 10), (13, 9), (13, 8)]
    elif wave == 1:        # tilted in
        arm = [(10, 12), (11, 11), (12, 10), (12, 9), (12, 8)]
    else:                  # tilted out
        arm = [(10, 12), (11, 11), (12, 10), (13, 10), (14, 9)]
    for ax, ay in arm:
        put(px, rx + ax, ry + ay, "B")
    hx, hy = arm[-1]
    put(px, rx + hx, ry + hy - 1, "h")
    # shadow (shrinks when bot bobs up)
    sw = 4 if bob else 5
    for x in range(-sw, sw + 1):
        put(px, rx + 6 + x, 25, "S")

    # --- chart --------------------------------------------------------
    cx, base = 28, 25
    for x in range(cx - 1, cx + 40):
        put(px, x, base, "X")
    for y in range(4, base + 1):
        put(px, cx - 1, y, "X")
    targets = [5, 8, 11, 15, 19]
    for i, tgt in enumerate(targets):
        delay = i * 0.08
        g = max(0.0, min(1.0, (t - delay) / 0.45))
        g = 1 - (1 - g) ** 3
        h = round(tgt * g)
        col, shade = ("G", "g") if i % 2 else ("I", "i")
        bx = cx + 2 + i * 7
        for y in range(h):
            for x in range(4):
                put(px, bx + x, base - 1 - y, shade if x == 3 else col)
    # trend arrow appears after bars grow
    if t > 0.55:
        prog = min(1.0, (t - 0.55) / 0.25)
        pts = []
        for i, tgt in enumerate(targets):
            pts.append((cx + 4 + i * 7, base - 3 - tgt))
        n = int(prog * (len(pts) - 1) * 7)
        drawn = 0
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            steps = max(abs(x1 - x0), abs(y1 - y0))
            for s in range(steps):
                if drawn > n:
                    break
                put(px, x0 + round((x1 - x0) * s / steps), y0 + round((y1 - y0) * s / steps), "Y")
                drawn += 1
        if prog >= 1:
            ex, ey = pts[-1]
            for (dx, dy) in [(0, 0), (-1, 0), (-2, 0), (0, 1), (0, 2), (1, -1), (-1, 1)]:
                put(px, ex + dx + 1, ey + dy - 1, "Y")

    # --- sparkles -----------------------------------------------------
    sparks = [(22, 5, "Y", 0), (3, 4, "P", 5), (24, 18, "P", 10), (70, 7, "Y", 14), (66, 2, "P", 3)]
    for sx, sy, c, ph in sparks:
        s = (f + ph) % 12
        if s < 2:
            put(px, sx, sy, c)
        elif s < 5:
            for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
                put(px, sx + dx, sy + dy, c)
        elif s < 6:
            put(px, sx, sy, c)

    # render to indexed image
    img = Image.new("P", (W * U, H * U), 0)
    flat = []
    for k in KEYS:
        flat += PAL[k]
    flat += [0] * (768 - len(flat))
    img.putpalette(flat)
    d = ImageDraw.Draw(img)
    for y in range(H):
        for x in range(W):
            k = px[y][x]
            if k != "t":
                d.rectangle([x * U, y * U, x * U + U - 1, y * U + U - 1], fill=KEYS.index(k))
    return img


frames = [frame(f) for f in range(FRAMES)]
durations = [110] * FRAMES
durations[-1] = 1400  # hold the finished chart
frames[0].save(
    "assets/hero.gif", save_all=True, append_images=frames[1:],
    duration=durations, loop=0, transparency=0, disposal=2, optimize=False,
)
print("ok")
