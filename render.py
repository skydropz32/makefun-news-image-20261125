"""The Daily Dispatch front page renderer, written from scratch.

Pure Python standard library. Draws a 1024x1024 newspaper front page
summing up Wednesday 25 November 2026 into PNG bytes.

Layout: masthead, dateline, lead story (Shenzhou-24 / Pakistan's first
astronaut), three mid stories (markets, Riyadh, the Gulf), two lower
stories (Australia, Bangladesh), an IN BRIEF band and a footer. Every
figure comes from the verified brief for 25 November 2026.
"""

import struct
import zlib

W = 1024
H = 1024

PAPER = (245, 239, 223)
INK = (25, 25, 25)
RED = (158, 27, 30)
NAVY = (23, 50, 77)
BLUE = (43, 93, 138)
SKY = (174, 205, 227)
GRAY = (107, 98, 87)
RULE = (185, 173, 151)
WHITE = (255, 255, 255)
FLAME = (232, 122, 36)
GOLD = (214, 164, 65)

# 5x7 pixel font, one row per string, "#" set, " " clear.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
}


def text_width(text, scale):
    """Width in pixels of text at the given scale (6 units per glyph)."""
    if not text:
        return 0
    return len(text) * 6 * scale - scale


def wrap_text(text, max_width, scale):
    """Word-wrap text to lines no wider than max_width pixels."""
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if text_width(trial, scale) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


class Canvas:
    """An RGB raster with simple vector drawing helpers."""

    def __init__(self, width, height, background):
        self.width = width
        self.height = height
        self.buf = bytearray(background * (width * height))
        self.clip = None

    def set_clip(self, x0, y0, x1, y1):
        self.clip = (x0, y0, x1, y1)

    def clear_clip(self):
        self.clip = None

    def px(self, x, y, color):
        if self.clip is not None:
            cx0, cy0, cx1, cy1 = self.clip
            if not (cx0 <= x < cx1 and cy0 <= y < cy1):
                return
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.buf[i] = color[0]
            self.buf[i + 1] = color[1]
            self.buf[i + 2] = color[2]

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.px(xx, yy, color)

    def hline(self, x, y, w, color, thick=1):
        self.rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.rect(x, y, thick, h, color)

    def line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.px(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        """Filled triangle by horizontal scanlines."""
        pts = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        if ay == cy:
            return
        for yy in range(ay, cy + 1):
            if yy < by:
                xa = ax + (bx - ax) * (yy - ay) / (by - ay) if by != ay else ax
                xb = ax + (cx - ax) * (yy - ay) / (cy - ay)
            else:
                xa = bx + (cx - bx) * (yy - by) / (cy - by) if cy != by else bx
                xb = ax + (cx - ax) * (yy - ay) / (cy - ay)
            lo, hi = (xa, xb) if xa <= xb else (xb, xa)
            for xx in range(int(lo), int(hi) + 1):
                self.px(xx, yy, color)

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                    self.px(xx, yy, color)

    def ring(self, cx, cy, r, color, thick=2):
        for yy in range(cy - r - thick, cy + r + thick + 1):
            for xx in range(cx - r - thick, cx + r + thick + 1):
                d2 = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
                if (r - thick) * (r - thick) <= d2 <= (r + thick) * (r + thick):
                    self.px(xx, yy, color)

    def text(self, x, y, text, scale, color):
        """Draw text; returns the x just past the last glyph."""
        cx = x
        for ch in text:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += 6 * scale
        return cx

    def text_center(self, cx, y, text, scale, color):
        x = cx - text_width(text, scale) // 2
        return self.text(x, y, text, scale, color)

    def paragraph(self, x, y, text, max_width, scale, color, leading):
        """Draw wrapped text; returns the y just past the last line."""
        yy = y
        for line in wrap_text(text, max_width, scale):
            self.text(x, yy, line, scale, color)
            yy += leading
        return yy


def png_bytes(canvas):
    """Encode the canvas as a deterministic PNG (filter 0, zlib level 6)."""
    raw = bytearray()
    stride = canvas.width * 3
    for yy in range(canvas.height):
        raw.append(0)
        raw += canvas.buf[yy * stride:(yy + 1) * stride]
    comp = zlib.compress(bytes(raw), 6)

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", canvas.width, canvas.height, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


# ---------------------------------------------------------------- pictures

def draw_rocket(cv, x, y, w, h):
    """Shenzhou capsule rocket on a night panel with stars and Earth."""
    cv.rect(x, y, w, h, NAVY)
    for sx, sy in ((12, 14), (44, 30), (w - 20, 12), (w - 46, 44),
                   (24, 58), (w - 30, 70), (58, 10)):
        cv.rect(x + sx, y + sy, 3, 3, WHITE)
        cv.rect(x + sx + 1, y + sy - 3, 1, 9, WHITE)
        cv.rect(x + sx - 3, y + sy + 1, 9, 1, WHITE)
    cx = x + w // 2
    # Earth arc along the bottom, clipped to the panel so it never
    # spills over the stories below.
    cv.set_clip(x, y, x + w, y + h)
    cv.ring(cx, y + h + 150, 190, SKY, 3)
    cv.disc(cx - 58, y + h - 26, 10, SKY)
    cv.disc(cx + 64, y + h - 18, 7, SKY)
    cv.clear_clip()
    # Rocket body.
    top = y + 22
    body_w = 34
    cv.triangle(cx, top - 16, cx - body_w // 2, top + 14,
                cx + body_w // 2, top + 14, RED)
    cv.rect(cx - body_w // 2, top + 14, body_w, 74, WHITE)
    cv.rect(cx - body_w // 2, top + 14, body_w, 8, RED)
    cv.disc(cx, top + 48, 9, BLUE)
    cv.disc(cx, top + 48, 5, SKY)
    cv.triangle(cx - body_w // 2, top + 88, cx - body_w // 2 - 16, top + 112,
                cx - body_w // 2, top + 112, RED)
    cv.triangle(cx + body_w // 2, top + 88, cx + body_w // 2 + 16, top + 112,
                cx + body_w // 2, top + 112, RED)
    cv.triangle(cx - 12, top + 112, cx + 12, top + 112, cx, top + 142, FLAME)
    cv.triangle(cx - 6, top + 112, cx + 6, top + 112, cx, top + 128, GOLD)


def draw_chart(cv, x, y, w, h):
    """Falling market line on white panel."""
    cv.rect(x, y, w, h, WHITE)
    cv.rect(x, y, w, h, RULE)
    cv.rect(x + 2, y + 2, w - 4, h - 4, WHITE)
    cv.hline(x + 10, y + h - 12, w - 20, GRAY, 2)
    cv.vline(x + 10, y + 10, h - 22, GRAY, 2)
    pts = [(x + 14, y + 22), (x + 34, y + 30), (x + 52, y + 26),
           (x + 72, y + 44), (x + 90, y + 58), (x + w - 14, y + h - 24)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        cv.line(ax, ay, bx, by, RED)
        cv.line(ax, ay + 1, bx, by + 1, RED)
    ex, ey = pts[-1]
    cv.triangle(ex, ey, ex - 10, ey - 2, ex - 2, ey + 8, RED)


def draw_tower(cv, x, y, w, h):
    """Riyadh financial-district tower with a drone above it."""
    cv.rect(x, y, w, h, WHITE)
    cv.rect(x, y, w, h, RULE)
    cv.rect(x + 2, y + 2, w - 4, h - 4, WHITE)
    tx = x + w // 2
    cv.rect(tx - 16, y + h - 58, 32, 58, NAVY)
    cv.rect(tx - 11, y + h - 72, 22, 16, NAVY)
    cv.rect(tx - 6, y + h - 84, 12, 14, NAVY)
    cv.line(tx, y + h - 84, tx, y + 16, NAVY)
    for wy in range(y + h - 52, y + h - 6, 9):
        cv.rect(tx - 12, wy, 24, 3, SKY)
    dx, dy = x + w - 30, y + 14
    cv.rect(dx - 8, dy, 17, 3, INK)
    cv.rect(dx - 2, dy - 2, 5, 7, INK)
    cv.line(dx - 12, dy - 6, dx + 13, dy + 8, INK)
    cv.line(dx + 13, dy - 6, dx - 12, dy + 8, INK)


def draw_barrel(cv, x, y, w, h):
    """Oil barrel with a flame, on a white panel."""
    cv.rect(x, y, w, h, WHITE)
    cv.rect(x, y, w, h, RULE)
    cv.rect(x + 2, y + 2, w - 4, h - 4, WHITE)
    bx = x + w // 2 - 20
    cv.rect(bx, y + 30, 40, 52, NAVY)
    cv.rect(bx, y + 30, 40, 6, BLUE)
    cv.rect(bx, y + 52, 40, 4, BLUE)
    cv.rect(bx, y + 72, 40, 4, BLUE)
    cv.triangle(bx + 20, y + 8, bx + 12, y + 26, bx + 28, y + 26, FLAME)
    cv.triangle(bx + 20, y + 14, bx + 15, y + 26, bx + 25, y + 26, GOLD)


def draw_parliament(cv, x, y, w, h):
    """Parliament house front: roof triangle and columns."""
    cv.rect(x, y, w, h, WHITE)
    cv.rect(x, y, w, h, RULE)
    cv.rect(x + 2, y + 2, w - 4, h - 4, WHITE)
    cx = x + w // 2
    cv.triangle(cx - 44, y + 34, cx + 44, y + 34, cx, y + 12, NAVY)
    for i in range(5):
        colx = cx - 40 + i * 20
        cv.rect(colx, y + 38, 6, 34, NAVY)
    cv.rect(cx - 46, y + 34, 92, 4, NAVY)
    cv.rect(cx - 46, y + 72, 92, 5, NAVY)


def draw_plane(cv, x, y, w, h):
    """Airliner in flight, nose to the right."""
    cv.rect(x, y, w, h, WHITE)
    cv.rect(x, y, w, h, RULE)
    cv.rect(x + 2, y + 2, w - 4, h - 4, WHITE)
    cx, cy = x + w // 2, y + h // 2
    cv.rect(cx - 52, cy - 5, 96, 10, NAVY)
    cv.triangle(cx + 44, cy - 5, cx + 62, cy, cx + 44, cy + 5, NAVY)
    cv.triangle(cx - 10, cy - 5, cx + 6, cy - 26, cx + 14, cy - 5, NAVY)
    cv.triangle(cx - 2, cy + 5, cx + 10, cy + 22, cx + 16, cy + 5, NAVY)
    cv.triangle(cx - 52, cy - 5, cx - 64, cy - 18, cx - 52, cy + 2, NAVY)
    for wx in range(cx - 40, cx + 36, 12):
        cv.rect(wx, cy - 2, 5, 4, SKY)


# ---------------------------------------------------------------- content

# Bottom edge of the drawn layout after the last render_page() call.
LAST_Y = 0

LEAD_HEADLINE = ("PAKISTAN'S FIRST", "ASTRONAUT IN ORBIT")
LEAD_SUB = ("SHENZHOU-24 CARRIES MUHAMMAD ZEESHAN ALI TO CHINA'S "
            "TIANGONG STATION, THE FIRST FOREIGN ASTRONAUT ABOARD. "
            "HE WILL RUN FOUR PAKISTANI BIOTECH EXPERIMENTS.")
LEAD_BODY = ("LONG MARCH-2F LIFTED OFF FROM JIUQUAN AT 08:18 LOCAL TIME "
             "WITH COMMANDER TANG HONGBO, WU YI AND ALI, 40, A PAKISTANI "
             "AIR FORCE PILOT. ALI WILL STAY FIVE TO TEN DAYS AND RETURN "
             "ABOARD SHENZHOU-23.")

MID_STORIES = [
    ("MARKETS", "NVIDIA SLIDES 6% AS RALLY FADES",
     "THE NASDAQ FELL 1.5% AND THE S&P 500 0.5% A DAY AFTER NVIDIA'S "
     "31.5% SURGE. MICRON FELL 11% AND HPE 16% AS A U.S. TARIFF PROBE "
     "REPORT WEIGHED ON CHIPMAKERS.", draw_chart),
    ("RIYADH", "DRONE HITS RIYADH'S TALLEST TOWER",
     "ELEVEN PEOPLE WERE WOUNDED IN THE SECOND STRIKE ON THE CAPITAL'S "
     "FINANCIAL DISTRICT IN A WEEK. SAUDI-LED FORCES VOWED A FIRM "
     "RESPONSE.", draw_tower),
    ("THE GULF", "IRAN VOWS TO FIGHT SEA BLOCKADE",
     "TEHRAN SAID IT WOULD USE ALL AVAILABLE MEANS AS THE STRAIT OF "
     "HORMUZ STAYS SHUT. BRENT CRUDE EASED 43 CENTS TO $90.97 A "
     "BARREL.", draw_barrel),
]

LOW_STORIES = [
    ("AUSTRALIA", "CANBERRA APOLOGISES TO LGBTQ VETERANS",
     "THE GOVERNMENT SAID SORRY IN PARLIAMENT FOR DECADES OF "
     "DISCRIMINATION AGAINST GAY AND LESBIAN SERVICE MEMBERS.",
     draw_parliament),
    ("BANGLADESH", "HASINA PLANS RETURN ON 16 DECEMBER",
     "THE FORMER PRIME MINISTER, 79, PLANS TO COME HOME FROM EXILE IN "
     "INDIA ON VICTORY DAY. MINISTERS SAY SHE WILL BE ARRESTED.",
     draw_plane),
]

IN_BRIEF = [
    ("FRANCE", "SARKOZY AND WIFE CARLA BRUNI ORDERED TO TRIAL OVER "
     "CORRUPTION."),
    ("BALTIC", "KYIV SAYS IT HIT A RUSSIAN CARGO SHIP IN THE GULF OF "
     "FINLAND."),
    ("HEALTH", "AIDS DEATHS 570,000 IN 2025, A 20-YEAR LOW; FUNDS -18%."),
]


def render_page():
    """Draw the whole front page and return deterministic PNG bytes."""
    global LAST_Y
    cv = Canvas(W, H, PAPER)
    mx = 36
    right = W - mx
    inner = right - mx
    y = 24

    # Masthead.
    cv.text_center(W // 2, y, "THE DAILY DISPATCH", 7, INK)
    y += 56
    cv.hline(mx, y, inner, INK, 2)
    y += 8
    cv.text(mx, y, "RABU, 25 NOVEMBER 2026", 2, INK)
    cv.text(right - text_width("VOL. 1 - NO. 25", 2), y,
            "VOL. 1 - NO. 25", 2, INK)
    y += 20
    cv.hline(mx, y, inner, INK, 5)
    y += 4
    cv.hline(mx, y, inner, INK, 2)
    y += 10

    # Lead story: text left, rocket art right.
    art_w = 300
    art_h = 168
    text_w = inner - art_w - 24
    ly = y
    cv.text(mx, ly, "SPACE", 2, RED)
    ly += 20
    for line in LEAD_HEADLINE:
        cv.text(mx, ly, line, 5, INK)
        ly += 38
    ly += 4
    ly = cv.paragraph(mx, ly, LEAD_SUB, text_w, 2, INK, 18)
    ly += 6
    ly = cv.paragraph(mx, ly, LEAD_BODY, text_w, 2, GRAY, 17)
    draw_rocket(cv, right - art_w, y + 16, art_w, art_h)
    y = max(ly, y + 16 + art_h) + 10
    cv.hline(mx, y, inner, RULE, 2)
    y += 8

    # Three mid stories in columns.
    gap = 24
    col_w = (inner - 2 * gap) // 3
    col_tops = []
    for i, (kicker, head, body, art) in enumerate(MID_STORIES):
        cx0 = mx + i * (col_w + gap)
        cy = y
        cv.text(cx0, cy, kicker, 2, RED)
        cy += 20
        for line in wrap_text(head, col_w, 3):
            cv.text(cx0, cy, line, 3, INK)
            cy += 24
        cy += 4
        art(cv, cx0, cy, col_w, 72)
        cy += 72 + 8
        cy = cv.paragraph(cx0, cy, body, col_w, 2, INK, 17)
        col_tops.append(cy)
    y = max(col_tops) + 8
    cv.hline(mx, y, inner, RULE, 2)
    y += 8

    # Two lower stories in columns.
    col_w2 = (inner - gap) // 2
    low_tops = []
    for i, (kicker, head, body, art) in enumerate(LOW_STORIES):
        cx0 = mx + i * (col_w2 + gap)
        cy = y
        cv.text(cx0, cy, kicker, 2, RED)
        cy += 20
        for line in wrap_text(head, col_w2, 3):
            cv.text(cx0, cy, line, 3, INK)
            cy += 24
        cy += 4
        art(cv, cx0, cy, 150, 64)
        cy2 = cv.paragraph(cx0 + 164, cy + 2, body, col_w2 - 164, 2, INK, 17)
        low_tops.append(max(cy + 64, cy2))
    y = max(low_tops) + 8
    cv.hline(mx, y, inner, RULE, 2)
    y += 8

    # IN BRIEF band.
    band_h = 104
    cv.rect(mx, y, inner, band_h, NAVY)
    cv.text(mx + 16, y + 12, "IN BRIEF", 2, GOLD)
    bcol_w = (inner - 32 - 2 * gap) // 3
    for i, (kicker, text) in enumerate(IN_BRIEF):
        bx = mx + 16 + i * (bcol_w + gap)
        cv.text(bx, y + 36, kicker, 2, GOLD)
        cv.paragraph(bx, y + 52, text, bcol_w, 2, WHITE, 17)
    y += band_h + 8

    # Footer.
    cv.hline(mx, y, inner, INK, 2)
    y += 6
    cv.text_center(
        W // 2, y,
        "ALL FIGURES VERIFIED AGAINST PRIMARY SOURCES: REUTERS, XINHUA,",
        2, GRAY)
    y += 16
    cv.text_center(
        W // 2, y,
        "SAUDI CIVIL DEFENSE, UNAIDS - THE DAILY DISPATCH",
        2, GRAY)
    LAST_Y = y + 16
    return png_bytes(cv)
