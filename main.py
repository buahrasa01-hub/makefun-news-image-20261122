#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""make.fun entry news-image-20261122: "THE WORLD IN ONE IMAGE".

Draws a 1024x1024 newspaper front page that sums up the world news of
Sunday 22 November 2026: a navy masthead that names the day, six story
panels with flat vector scenes, and a sources footer.  Pure standard
library, no network, no external image: every pixel comes from this
program's own code, and two runs write identical bytes.
"""

import os
import struct
import zlib

W = 1024
H = 1024
STRIDE = W * 3

PAPER = (247, 243, 233)
EDGE = (184, 176, 162)
NAVY = (20, 32, 58)
INK = (24, 24, 28)
WHITE = (255, 255, 255)
CAPINK = (58, 56, 54)

CANVAS = bytearray(STRIDE * H)
CLIP = (0, 0, W, H)

# ---------------------------------------------------------------- drawing --

def set_clip(x0, y0, x1, y1):
    global CLIP
    CLIP = (int(x0), int(y0), int(x1), int(y1))


def reset_clip():
    global CLIP
    CLIP = (0, 0, W, H)


def fill_rect(x, y, w, h, c):
    if w <= 0 or h <= 0:
        return
    x = int(x)
    y = int(y)
    w = int(w)
    h = int(h)
    cx0, cy0, cx1, cy1 = CLIP
    if x < cx0:
        w -= cx0 - x
        x = cx0
    if y < cy0:
        h -= cy0 - y
        y = cy0
    if x + w > cx1:
        w = cx1 - x
    if y + h > cy1:
        h = cy1 - y
    if w <= 0 or h <= 0:
        return
    row = bytes(c) * w
    n = w * 3
    i = (y * W + x) * 3
    for _ in range(h):
        CANVAS[i:i + n] = row
        i += STRIDE


def fill_circle(cx, cy, r, c):
    cx = int(cx)
    cy = int(cy)
    r = int(r)
    if r < 0:
        return
    for dy in range(-r, r + 1):
        lim = r * r - dy * dy
        dx = 0
        while (dx + 1) * (dx + 1) + dy * dy <= lim:
            dx += 1
        fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)


def fill_ring(cx, cy, r, thick, c):
    fill_circle(cx, cy, r, c)
    fill_circle(cx, cy, r - thick, (0, 0, 0))


def fill_tri(p0, p1, p2, c):
    ax, ay = p0
    bx, by = p1
    cx, cy = p2
    top = int(min(ay, by, cy))
    bot = int(max(ay, by, cy))
    for yy in range(top, bot + 1):
        xs = []
        for (x0, y0), (x1, y1) in ((p0, p1), (p1, p2), (p2, p0)):
            if y0 == y1:
                continue
            if min(y0, y1) <= yy < max(y0, y1):
                t = (yy - y0) / (y1 - y0)
                xs.append(x0 + t * (x1 - x0))
        if len(xs) >= 2:
            xs.sort()
            xa = int(xs[0])
            xb = int(xs[-1])
            fill_rect(xa, yy, xb - xa + 1, 1, c)


def fill_quad(p0, p1, p2, p3, c):
    fill_tri(p0, p1, p2, c)
    fill_tri(p0, p2, p3, c)


def draw_line(x0, y0, x1, y1, thick, c):
    x0 = int(x0)
    y0 = int(y0)
    x1 = int(x1)
    y1 = int(y1)
    steps = max(abs(x1 - x0), abs(y1 - y0))
    half = thick // 2
    if steps == 0:
        fill_rect(x0 - half, y0 - half, thick, thick, c)
        return
    for i in range(steps + 1):
        t = i / steps
        fill_rect(int(round(x0 + t * (x1 - x0))) - half,
                  int(round(y0 + t * (y1 - y0))) - half,
                  thick, thick, c)


UNIT = (
    1000, 0, 995, 87, 978, 208, 951, 309, 914, 407, 866, 500, 809, 588,
    707, 707, 588, 809, 500, 866, 407, 914, 309, 951, 208, 978, 87, 995,
    0, 1000, -87, 995, -208, 978, -309, 951, -407, 914, -500, 866, -588, 809,
    -707, 707, -809, 588, -866, 500, -914, 407, -951, 309, -978, 208, -995, 87,
    -1000, 0, -995, -87, -978, -208, -951, -309, -914, -407, -866, -500,
    -809, -588, -707, -707, -588, -809, -500, -866, -407, -914, -309, -951,
    -208, -978, -87, -995, 0, -1000, 87, -995, 208, -978, 309, -951, 407, -914,
    500, -866, 588, -809, 707, -707, 809, -588,
)


def draw_arc(cx, cy, r, thick, i0, i1, c, step=2):
    n = len(UNIT) // 2
    i = i0
    while i <= i1:
        co = UNIT[(i % n) * 2]
        si = UNIT[(i % n) * 2 + 1]
        fill_rect(cx + co * (r - thick) // 1000, cy + si * (r - thick) // 1000,
                  thick + 2, thick + 2, c)
        i += step


# ------------------------------------------------------------------- font --

FONT = {
    'A': ('01110', '10001', '10001', '11111', '10001', '10001', '10001'),
    'B': ('11110', '10001', '10001', '11110', '10001', '10001', '11110'),
    'C': ('01110', '10001', '10000', '10000', '10000', '10001', '01110'),
    'D': ('11110', '10001', '10001', '10001', '10001', '10001', '11110'),
    'E': ('11111', '10000', '10000', '11110', '10000', '10000', '11111'),
    'F': ('11111', '10000', '10000', '11110', '10000', '10000', '10000'),
    'G': ('01110', '10001', '10000', '10111', '10001', '10001', '01111'),
    'H': ('10001', '10001', '10001', '11111', '10001', '10001', '10001'),
    'I': ('11111', '00100', '00100', '00100', '00100', '00100', '11111'),
    'J': ('00111', '00010', '00010', '00010', '00010', '10010', '01100'),
    'K': ('10001', '10010', '10100', '11000', '10100', '10010', '10001'),
    'L': ('10000', '10000', '10000', '10000', '10000', '10000', '11111'),
    'M': ('10001', '11011', '10101', '10101', '10001', '10001', '10001'),
    'N': ('10001', '11001', '10101', '10011', '10001', '10001', '10001'),
    'O': ('01110', '10001', '10001', '10001', '10001', '10001', '01110'),
    'P': ('11110', '10001', '10001', '11110', '10000', '10000', '10000'),
    'Q': ('01110', '10001', '10001', '10001', '10101', '10010', '01101'),
    'R': ('11110', '10001', '10001', '11110', '10100', '10010', '10001'),
    'S': ('01111', '10000', '10000', '01110', '00001', '00001', '11110'),
    'T': ('11111', '00100', '00100', '00100', '00100', '00100', '00100'),
    'U': ('10001', '10001', '10001', '10001', '10001', '10001', '01110'),
    'V': ('10001', '10001', '10001', '10001', '10001', '01010', '00100'),
    'W': ('10001', '10001', '10001', '10101', '10101', '11011', '10001'),
    'X': ('10001', '10001', '01010', '00100', '01010', '10001', '10001'),
    'Y': ('10001', '10001', '01010', '00100', '00100', '00100', '00100'),
    'Z': ('11111', '00001', '00010', '00100', '01000', '10000', '11111'),
    '0': ('01110', '10001', '10011', '10101', '11001', '10001', '01110'),
    '1': ('00100', '01100', '00100', '00100', '00100', '00100', '01110'),
    '2': ('01110', '10001', '00001', '00010', '00100', '01000', '11111'),
    '3': ('11111', '00010', '00100', '00010', '00001', '10001', '01110'),
    '4': ('00010', '00110', '01010', '10010', '11111', '00010', '00010'),
    '5': ('11111', '10000', '11110', '00001', '00001', '10001', '01110'),
    '6': ('00110', '01000', '10000', '11110', '10001', '10001', '01110'),
    '7': ('11111', '00001', '00010', '00100', '01000', '01000', '01000'),
    '8': ('01110', '10001', '10001', '01110', '10001', '10001', '01110'),
    '9': ('01110', '10001', '10001', '01111', '00001', '00010', '01100'),
    ' ': ('00000', '00000', '00000', '00000', '00000', '00000', '00000'),
    '.': ('00000', '00000', '00000', '00000', '00000', '01100', '01100'),
    ',': ('00000', '00000', '00000', '00000', '00110', '00110', '01100'),
    ':': ('00000', '01100', '01100', '00000', '01100', '01100', '00000'),
    ';': ('00000', '01100', '01100', '00000', '01100', '00110', '01100'),
    '!': ('00100', '00100', '00100', '00100', '00100', '00000', '00100'),
    '?': ('01110', '10001', '00001', '00010', '00100', '00000', '00100'),
    "'": ('00100', '00100', '01000', '00000', '00000', '00000', '00000'),
    '-': ('00000', '00000', '00000', '11111', '00000', '00000', '00000'),
    '/': ('00001', '00010', '00010', '00100', '01000', '01000', '10000'),
    '(': ('00010', '00100', '01000', '01000', '01000', '00100', '00010'),
    ')': ('01000', '00100', '00010', '00010', '00010', '00100', '01000'),
    '%': ('11001', '11011', '00010', '00100', '01000', '11011', '10011'),
    '&': ('01100', '10010', '10100', '01000', '10101', '10010', '01101'),
    '+': ('00000', '00100', '00100', '11111', '00100', '00100', '00000'),
    '=': ('00000', '00000', '11111', '00000', '11111', '00000', '00000'),
    '$': ('00100', '01111', '10100', '01110', '00101', '11110', '00100'),
}


def text_width(s, scale, tracking=None):
    if tracking is None:
        tracking = scale
    n = len(s)
    if n == 0:
        return 0
    return n * 5 * scale + (n - 1) * tracking


def draw_text(x, y, s, scale, c, tracking=None):
    if tracking is None:
        tracking = scale
    cx = x
    for ch in s.upper():
        g = FONT.get(ch)
        if g is not None:
            for r in range(7):
                row = g[r]
                i = 0
                while i < 5:
                    if row[i] == '1':
                        run = 1
                        while i + run < 5 and row[i + run] == '1':
                            run += 1
                        fill_rect(cx + i * scale, y + r * scale, run * scale, scale, c)
                        i += run
                    else:
                        i += 1
        cx += 5 * scale + tracking
    return text_width(s, scale, tracking)


def draw_text_center(cx, y, s, scale, c, tracking=None):
    w = text_width(s, scale, tracking)
    return draw_text(cx - w // 2, y, s, scale, c, tracking)


def wrap_fit(text, maxw, scale, maxlines):
    words = text.split()
    lines = []
    i = 0
    while i < len(words) and len(lines) < maxlines:
        cur = words[i]
        i += 1
        while i < len(words) and text_width(cur + ' ' + words[i], scale) <= maxw:
            cur = cur + ' ' + words[i]
            i += 1
        lines.append(cur)
    return lines


# ----------------------------------------------------------------- scenes --

def missile(x, y):
    fill_tri((x, y), (x - 16, y + 5), (x, y + 10), (255, 156, 56))
    fill_tri((x, y + 2), (x - 8, y + 5), (x, y + 8), (255, 222, 120))
    fill_rect(x, y, 42, 10, (196, 62, 58))
    fill_tri((x + 42, y), (x + 42, y + 10), (x + 56, y + 5), (216, 84, 76))
    fill_tri((x, y), (x - 8, y - 7), (x + 6, y), (170, 48, 46))
    fill_tri((x, y + 10), (x - 8, y + 17), (x + 6, y + 10), (170, 48, 46))


def drone(x, y):
    fill_rect(x, y, 26, 4, (72, 76, 86))
    fill_rect(x + 11, y + 4, 5, 7, (58, 62, 72))
    fill_rect(x + 4, y + 11, 18, 3, (72, 76, 86))
    fill_circle(x + 2, y + 2, 3, (150, 156, 166))
    fill_circle(x + 24, y + 2, 3, (150, 156, 166))


def scene_gulf(x, y, sw, sh):
    fill_rect(x, y, 472, 78, (46, 60, 100))
    fill_rect(x, y, 472, 24, (66, 78, 120))
    fill_rect(x, y + 78, 472, 56, (221, 195, 142))
    fill_circle(x + 392, y + 90, 26, (238, 162, 94))
    # air-defence radar site
    fill_rect(x + 92, y + 50, 6, 46, (176, 182, 192))
    fill_circle(x + 78, y + 44, 25, (216, 221, 229))
    fill_circle(x + 78, y + 44, 16, (46, 60, 100))
    fill_circle(x + 78, y + 44, 5, (200, 206, 216))
    fill_quad((x + 68, y + 96), (x + 112, y + 96), (x + 118, y + 126),
              (x + 62, y + 126), (168, 174, 184))
    # shield over the base
    fill_circle(x + 232, y + 108, 44, (86, 146, 214))
    fill_circle(x + 232, y + 108, 32, (132, 180, 234))
    fill_rect(x + 234, y + 104, 46, 46, (221, 195, 142))
    fill_rect(x + 186, y + 108, 100, 42, (221, 195, 142))
    # incoming missiles and drones
    missile(x + 296, y + 22)
    missile(x + 268, y + 58)
    missile(x + 372, y + 44)
    drone(x + 196, y + 16)
    drone(x + 380, y + 8)
    # struck industrial plant with fire and smoke
    fill_rect(x + 336, y + 92, 88, 42, (104, 108, 118))
    fill_rect(x + 336, y + 92, 88, 6, (88, 92, 102))
    fill_rect(x + 348, y + 76, 14, 18, (96, 100, 110))
    fill_rect(x + 372, y + 82, 12, 12, (96, 100, 110))
    fill_circle(x + 358, y + 102, 13, (248, 146, 48))
    fill_tri((x + 346, y + 106), (x + 358, y + 78), (x + 372, y + 106), (255, 198, 76))
    fill_circle(x + 388, y + 74, 11, (176, 178, 186))
    fill_circle(x + 404, y + 56, 14, (188, 190, 198))
    fill_circle(x + 424, y + 38, 16, (198, 200, 208))
    fill_circle(x + 446, y + 20, 18, (208, 210, 218))


def window_grid(bx, by, bw, bh, seed):
    for wy in range(by + 10, by + bh - 10, 18):
        for wx in range(bx + 8, bx + bw - 10, 16):
            if ((wx - bx) // 16 + (wy - by) // 18 + seed) % 3 != 0:
                fill_rect(wx, wy, 7, 9, (250, 214, 126))


def scene_mexico(x, y, sw, sh):
    fill_rect(x, y, 472, 134, (18, 24, 46))
    fill_circle(x + 62, y + 26, 15, (232, 226, 190))
    fill_circle(x + 69, y + 21, 13, (18, 24, 46))
    # low buildings with lit windows
    lows = ((x + 4, 62, 84, 0), (x + 74, 48, 66, 1), (x + 128, 56, 92, 2),
            (x + 190, 44, 72, 0), (x + 240, 66, 96, 1), (x + 312, 52, 78, 2),
            (x + 370, 42, 64, 1), (x + 416, 52, 86, 0))
    for bx, bw, bh, seed in lows:
        fill_rect(bx, y + 134 - bh, bw, bh, (32, 38, 62))
        window_grid(bx, y + 134 - bh, bw, bh, seed)
    # street
    fill_rect(x, y + 116, 472, 18, (52, 54, 66))
    for dx in range(10, 452, 56):
        fill_rect(x + dx, y + 124, 26, 3, (216, 210, 176))
    # searchlight beam from the helicopter
    set_clip(x + 328, y + 44, x + 384, y + 116)
    fill_tri((x + 352, y + 44), (x + 340, y + 116), (x + 372, y + 116),
             (246, 233, 176))
    reset_clip()
    # helicopter: rotor, body, tail boom, tail rotor, skids
    fill_rect(x + 300, y + 6, 104, 4, (176, 182, 194))
    fill_rect(x + 348, y + 10, 6, 8, (140, 146, 158))
    fill_quad((x + 328, y + 18), (x + 386, y + 18), (x + 380, y + 40),
              (x + 334, y + 40), (74, 78, 90))
    fill_tri((x + 328, y + 20), (x + 310, y + 29), (x + 328, y + 38), (88, 92, 104))
    fill_quad((x + 382, y + 22), (x + 434, y + 18), (x + 434, y + 24),
              (x + 382, y + 36), (74, 78, 90))
    fill_rect(x + 430, y + 10, 4, 22, (100, 104, 116))
    fill_quad((x + 433, y + 10), (x + 444, y + 4), (x + 444, y + 10),
              (x + 433, y + 16), (140, 146, 158))
    fill_rect(x + 338, y + 42, 5, 8, (100, 104, 116))
    fill_rect(x + 370, y + 42, 5, 8, (100, 104, 116))
    fill_rect(x + 330, y + 50, 56, 3, (150, 156, 168))
    fill_rect(x + 342, y + 28, 26, 8, (150, 190, 226))
    # wanted poster
    fill_rect(x + 52, y + 56, 62, 74, (238, 234, 220))
    fill_rect(x + 52, y + 56, 62, 3, (70, 70, 74))
    fill_rect(x + 52, y + 127, 62, 3, (70, 70, 74))
    fill_rect(x + 52, y + 56, 3, 74, (70, 70, 74))
    fill_rect(x + 111, y + 56, 3, 74, (70, 70, 74))
    draw_text(x + 59, y + 63, "WANTED", 1, (40, 40, 44))
    fill_circle(x + 83, y + 92, 12, (58, 52, 48))
    fill_rect(x + 60, y + 107, 46, 3, (110, 106, 100))
    fill_rect(x + 66, y + 114, 34, 3, (110, 106, 100))
    # soldiers and the escorted prisoner
    for fx in (x + 152, x + 192):
        fill_rect(fx, y + 74, 20, 44, (52, 62, 52))
        fill_rect(fx - 3, y + 58, 26, 7, (38, 44, 38))
        fill_circle(fx + 10, y + 66, 8, (96, 78, 60))
        fill_rect(fx + 6, y + 92, 8, 26, (30, 34, 30))
        fill_rect(fx + 24, y + 70, 14, 4, (60, 60, 64))
        fill_rect(fx + 22, y + 62, 4, 14, (60, 60, 64))
    fill_rect(x + 236, y + 78, 22, 40, (78, 70, 62))
    fill_circle(x + 247, y + 70, 7, (110, 88, 68))
    fill_circle(x + 242, y + 118, 5, (198, 202, 210))
    fill_circle(x + 254, y + 118, 5, (198, 202, 210))
    fill_rect(x + 234, y + 86, 26, 5, (160, 164, 172))


def scene_climate(x, y, sw, sh):
    fill_rect(x, y, 472, 134, (226, 230, 238))
    fill_rect(x, y + 108, 472, 26, (196, 188, 170))
    fill_rect(x, y, 472, 10, (208, 214, 226))
    # summit banner with COP31
    fill_rect(x + 56, y + 18, 148, 66, (26, 78, 146))
    fill_rect(x + 56, y + 18, 148, 4, (16, 52, 104))
    fill_rect(x + 56, y + 80, 148, 4, (16, 52, 104))
    draw_text_center(x + 130, y + 38, "COP31", 3, (250, 250, 246))
    fill_rect(x + 74, y + 70, 112, 4, (250, 250, 246))
    # globe
    fill_circle(x + 268, y + 52, 30, (48, 112, 182))
    fill_circle(x + 258, y + 40, 10, (92, 168, 96))
    fill_circle(x + 280, y + 60, 8, (92, 168, 96))
    fill_circle(x + 262, y + 68, 6, (92, 168, 96))
    fill_rect(x + 238, y + 52, 60, 3, (150, 196, 232))
    fill_rect(x + 262, y + 22, 3, 60, (150, 196, 232))
    # oil barrel with a red cross over it
    fill_rect(x + 330, y + 30, 42, 56, (94, 96, 104))
    fill_rect(x + 330, y + 30, 42, 7, (128, 130, 138))
    fill_rect(x + 334, y + 56, 34, 8, (58, 60, 68))
    fill_rect(x + 336, y + 34, 4, 52, (110, 112, 120))
    fill_rect(x + 362, y + 34, 4, 52, (110, 112, 120))
    draw_line(x + 324, y + 24, x + 378, y + 92, 7, (206, 62, 58))
    draw_line(x + 378, y + 24, x + 324, y + 92, 7, (206, 62, 58))
    # mostly empty tables with a few delegates
    for tx, tlen in ((x + 20, 120), (x + 156, 120), (x + 292, 150)):
        fill_rect(tx, y + 92, tlen, 7, (156, 116, 78))
        fill_rect(tx + 8, y + 99, 6, 22, (128, 96, 66))
        fill_rect(tx + tlen - 14, y + 99, 6, 22, (128, 96, 66))
    for dx in (x + 44, x + 108, x + 196, x + 320, x + 392):
        fill_rect(dx, y + 108, 22, 26, (72, 84, 104))
        fill_circle(dx + 11, y + 101, 8, (216, 186, 152))


def scene_eu_indonesia(x, y, sw, sh):
    fill_rect(x, y, 472, 100, (152, 198, 236))
    fill_rect(x, y, 472, 12, (176, 214, 240))
    fill_rect(x, y + 100, 472, 34, (52, 110, 176))
    # EU flag: circle of twelve stars
    fill_rect(x + 34, y + 20, 96, 64, (18, 40, 132))
    for i in range(12):
        ax = (0, 9, 16, 18, 16, 9, 0, -9, -16, -18, -16, -9)[i]
        ay = (-18, -16, -9, 0, 9, 16, 18, 16, 9, 0, -9, -16)[i]
        fill_circle(x + 82 + ax, y + 52 + ay, 3, (250, 214, 70))
    # Indonesian flag
    fill_rect(x + 152, y + 20, 96, 32, (206, 52, 52))
    fill_rect(x + 152, y + 52, 96, 32, (244, 242, 238))
    fill_rect(x + 152, y + 20, 96, 2, (120, 120, 120))
    fill_rect(x + 152, y + 82, 96, 2, (120, 120, 120))
    # container ship
    fill_quad((x + 252, y + 100), (x + 468, y + 100), (x + 452, y + 128),
              (x + 268, y + 128), (36, 48, 84))
    fill_rect(x + 262, y + 100, 206, 6, (52, 66, 104))
    fill_rect(x + 420, y + 74, 34, 26, (226, 228, 232))
    fill_rect(x + 426, y + 80, 22, 8, (60, 80, 130))
    fills = ((70, 96, 150), (196, 78, 62), (66, 132, 88), (206, 150, 60),
             (150, 72, 130), (72, 110, 150))
    cx = x + 272
    for i in range(6):
        fill_rect(cx, y + 86, 22, 14, fills[i])
        cx += 24
    for i in range(5):
        fill_rect(x + 296 + i * 24, y + 72, 22, 14, fills[(i + 3) % 6])
    for wx in range(0, 464, 48):
        fill_rect(x + wx, y + 122, 30, 4, (96, 152, 208))


def scene_peru(x, y, sw, sh):
    fill_rect(x, y, 472, 134, (170, 206, 234))
    fill_rect(x, y, 472, 36, (146, 190, 228))
    fill_tri((x - 10, y + 134), (x + 140, y + 22), (x + 296, y + 134),
             (126, 132, 146))
    fill_tri((x + 150, y + 134), (x + 330, y + 8), (x + 486, y + 134),
             (104, 110, 126))
    fill_tri((x + 96, y + 58), (x + 140, y + 22), (x + 186, y + 58),
             (238, 240, 244))
    fill_tri((x + 282, y + 50), (x + 330, y + 8), (x + 382, y + 50),
             (238, 240, 244))
    fill_rect(x, y + 124, 472, 10, (156, 136, 112))
    # seismograph trace
    fill_rect(x + 16, y + 88, 190, 34, (250, 250, 246))
    fill_rect(x + 16, y + 88, 190, 2, (150, 148, 144))
    fill_rect(x + 16, y + 120, 190, 2, (150, 148, 144))
    fill_rect(x + 16, y + 88, 2, 34, (150, 148, 144))
    fill_rect(x + 204, y + 88, 2, 34, (150, 148, 144))
    pts = ((x + 24, y + 106), (x + 60, y + 106), (x + 72, y + 94),
           (x + 84, y + 118), (x + 92, y + 100), (x + 106, y + 108),
           (x + 130, y + 106), (x + 150, y + 106), (x + 162, y + 98),
           (x + 174, y + 112), (x + 198, y + 106))
    for i in range(len(pts) - 1):
        draw_line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], 2,
                  (34, 34, 40))
    # two office towers leaning apart in the shake
    fill_quad((x + 278, y + 52), (x + 298, y + 52), (x + 288, y + 130),
              (x + 268, y + 130), (200, 200, 208))
    fill_quad((x + 278, y + 52), (x + 298, y + 52), (x + 296, y + 60),
              (x + 276, y + 60), (232, 232, 238))
    fill_quad((x + 322, y + 40), (x + 346, y + 40), (x + 366, y + 130),
              (x + 342, y + 130), (166, 166, 176))
    fill_quad((x + 322, y + 40), (x + 346, y + 40), (x + 343, y + 48),
              (x + 319, y + 48), (210, 210, 218))
    fill_quad((x + 366, y + 40), (x + 342, y + 130), (x + 348, y + 130),
              (x + 372, y + 40), (128, 128, 138))
    for i in range(6):
        fill_rect(x + 276 - (i * 13) // 10, y + 68 + i * 10, 10, 6, (248, 242, 224))
        fill_rect(x + 324 + (i * 8) // 3, y + 58 + i * 12, 10, 6, (248, 242, 224))
    # a crack opening in the ground
    draw_line(x + 372, y + 128, x + 392, y + 120, 2, (120, 100, 80))
    draw_line(x + 392, y + 120, x + 410, y + 130, 2, (120, 100, 80))
    # people in the street
    for px, ph in ((x + 226, 40), (x + 248, 34), (x + 268, 44), (x + 412, 38),
                   (x + 434, 44), (x + 454, 34)):
        fill_rect(px, y + 134 - ph, 11, ph - 11, (58, 58, 70))
        fill_circle(px + 5, y + 134 - ph - 5, 6, (76, 74, 72))


def scene_usa(x, y, sw, sh):
    fill_rect(x, y, 472, 134, (44, 50, 66))
    fill_rect(x, y, 472, 10, (34, 40, 54))
    # monitor showing a broken padlock
    fill_rect(x + 24, y + 14, 220, 106, (24, 26, 32))
    fill_rect(x + 32, y + 22, 204, 90, (46, 92, 152))
    fill_rect(x + 32, y + 22, 204, 6, (30, 68, 120))
    pxc = x + 134
    pyc = y + 60
    fill_ring(pxc, pyc - 16, 17, 6, (216, 176, 64))
    fill_rect(x + 96, y + 60, 78, 40, (222, 182, 70))
    fill_rect(x + 96, y + 60, 78, 5, (188, 150, 52))
    fill_rect(x + 96, y + 95, 78, 5, (196, 160, 56))
    fill_circle(pxc + 1, y + 80, 7, (44, 44, 52))
    fill_rect(pxc - 2, y + 80, 6, 14, (44, 44, 52))
    # the break: severed left shackle arm, right arc displaced upward
    fill_ring(x + 134, y + 44, 17, 7, (216, 176, 64))
    fill_rect(x + 92, y + 46, 58, 26, (46, 92, 152))
    draw_arc(x + 143, y + 52, 19, 7, 47, 63, (216, 176, 64))
    draw_line(x + 118, y + 30, x + 132, y + 22, 3, (30, 30, 36))
    draw_line(x + 150, y + 22, x + 162, y + 30, 3, (30, 30, 36))
    # police shield
    fill_rect(x + 304, y + 26, 60, 50, (40, 74, 150))
    fill_tri((x + 304, y + 72), (x + 364, y + 72), (x + 334, y + 106),
             (40, 74, 150))
    fill_rect(x + 304, y + 26, 60, 5, (24, 48, 104))
    fill_circle(x + 334, y + 48, 13, (232, 200, 80))
    fill_tri((x + 322, y + 66), (x + 346, y + 66), (x + 334, y + 38),
             (24, 48, 104))
    fill_tri((x + 329, y + 42), (x + 339, y + 42), (x + 334, y + 62),
             (24, 48, 104))
    # record card with a fingerprint
    fill_rect(x + 380, y + 84, 84, 44, (238, 236, 228))
    fill_rect(x + 380, y + 84, 84, 3, (150, 148, 142))
    fill_rect(x + 380, y + 125, 84, 3, (150, 148, 142))
    for r, col in ((18, (46, 46, 52)), (14, (238, 236, 228)),
                   (10, (46, 46, 52)), (5, (238, 236, 228)),
                   (2, (46, 46, 52))):
        fill_circle(x + 422, y + 106, r, col)
    # files
    for fx, fy in ((x + 262, y + 108), (x + 288, y + 112), (x + 316, y + 106)):
        fill_rect(fx, fy, 18, 22, (222, 198, 142))
        fill_rect(fx, fy, 18, 4, (196, 170, 116))


# ------------------------------------------------------------- the pages --

def draw_panel(px, py, pw, ph, scene_fn, tag, tagcolour, headline, caption):
    fill_rect(px, py, pw, ph, (252, 250, 244))
    fill_rect(px, py, pw, 2, EDGE)
    fill_rect(px, py + ph - 2, pw, 2, EDGE)
    fill_rect(px, py, 2, ph, EDGE)
    fill_rect(px + pw - 2, py, 2, ph, EDGE)
    sx = px + 8
    sy = py + 8
    sw = pw - 16
    sh = 134
    fill_rect(sx, sy, sw, sh, PAPER)
    set_clip(sx, sy, sx + sw, sy + sh)
    scene_fn(sx, sy, sw, sh)
    reset_clip()
    fill_rect(sx, sy, sw, 2, (150, 146, 140))
    fill_rect(sx, sy + sh - 2, sw, 2, (150, 146, 140))
    fill_rect(sx, sy, 2, sh, (150, 146, 140))
    fill_rect(sx + sw - 2, sy, 2, sh, (150, 146, 140))
    # region chip
    cy = py + 148
    chipw = text_width(tag, 1) + 18
    fill_rect(px + 12, cy, chipw, 18, tagcolour)
    draw_text(px + 21, cy + 6, tag, 1, WHITE)
    # headline rule, headline and caption in dark ink on the paper background
    tx = px + 13
    tw = pw - 26
    fill_rect(tx, py + 172, tw - 26, 1, EDGE)
    hy = py + 178
    for i, line in enumerate(wrap_fit(headline, tw, 2, 2)):
        draw_text(tx, hy + i * 21, line, 2, INK)
    ky = py + 226
    for i, line in enumerate(wrap_fit(caption, tw, 1, 2)):
        draw_text(tx, ky + i * 11, line, 1, CAPINK)


def draw_masthead():
    fill_rect(0, 0, W, 140, NAVY)
    fill_rect(0, 0, W, 6, (10, 18, 36))
    draw_text_center(W // 2, 18, "THE WORLD IN ONE IMAGE", 6, WHITE)
    draw_text_center(W // 2, 78, "SUNDAY 22 NOVEMBER 2026", 4, (248, 216, 120),
                     tracking=2 * 4)
    fill_rect(160, 120, 704, 3, (120, 150, 200))


def draw_footer():
    fill_rect(0, H - 40, W, 40, PAPER)
    fill_rect(16, H - 40, W - 32, 2, EDGE)
    draw_text_center(W // 2, H - 26,
                     "SOURCES: REUTERS - AP - AFP - 22 NOVEMBER 2026",
                     1, CAPINK)


STORIES = (
    (scene_gulf, "GULF", (150, 60, 44),
     "IRAN MISSILE AND DRONE STRIKES ON US BASES IN BAHRAIN",
     "Iran says it hit two Patriot radars. US Central Command says the weapons were intercepted, with no US casualties. Bahrain reports a factory fire."),
    (scene_mexico, "MEXICO", (30, 104, 76),
     "MEXICO CAPTURES FBI MOST WANTED 'EL CHAPO ISIDRO'",
     "Fausto Isidro Meza Flores, an FBI most wanted with a $5 million reward, was seized in Guasave, Sinaloa. The raid left 11 dead and eight arrested."),
    (scene_climate, "CLIMATE", (14, 104, 104),
     "COP31 TALKS IN TURKEY GO INTO OVERTIME OVER FOSSIL FUELS",
     "The Antalya draft drops all mention of fossil fuels and a $120 billion adaptation target, after opposition from oil producers."),
    (scene_eu_indonesia, "EU-INDONESIA", (24, 52, 132),
     "EU AND INDONESIA SIGN TRADE DEAL AFTER TEN YEARS",
     "Signed in Brussels after ten years of talks, the pact ends duties on more than 90 percent of products and should take effect in early 2027."),
    (scene_peru, "PERU", (150, 96, 24),
     "MAGNITUDE 6.7 QUAKE SHAKES CENTRAL PERU",
     "The quake struck 34 km north of Junin at a depth of 108 km and was felt in Lima, where residents rushed into the streets. No damage was reported."),
    (scene_usa, "USA", (128, 32, 48),
     "FBI PROBES HACK OF ITS CRIME RECORDS DATABASE",
     "The apparent breach of the National Crime Information Center, first reported by CNN and confirmed to AP, is the second FBI system hit in months."),
)


def build_image():
    fill_rect(0, 0, W, H, PAPER)
    draw_masthead()
    draw_footer()
    pw = 488
    ph = 270
    for i, (scene_fn, tag, colour, head, cap) in enumerate(STORIES):
        px = 16 + (i % 2) * (pw + 16)
        py = 140 + (i // 2) * 286
        draw_panel(px, py, pw, ph, scene_fn, tag, colour, head, cap)


# ------------------------------------------------------------------- png ---

def png_chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff))


def png_bytes():
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += CANVAS[y * STRIDE:(y + 1) * STRIDE]
    return b"".join((
        b"\x89PNG\r\n\x1a\n",
        png_chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)),
        png_chunk(b"IDAT", zlib.compress(bytes(raw), 9)),
        png_chunk(b"IEND", b""),
    ))


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    build_image()
    data = png_bytes()
    with open(os.path.join(outdir, "entry.png"), "wb") as fh:
        fh.write(data)


if __name__ == "__main__":
    main()
