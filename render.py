#!/usr/bin/env python3
"""Render the news-image-20261125 front page (1024x1024 PNG) with Pillow.

Local build tool only: the entry program (main.py) is standard library only
and copies the committed entry.png, because the grader's sandbox is a
python:3.13-slim container with no Pillow installed. This script runs on the
build machine to produce entry.png from the verified stories below.

Every figure was verified against a primary/authority source on 25 Nov 2026:
Shenzhou-24 (Reuters/Xinhua/CMSA), markets (Reuters Trading Day), Riyadh
(Reuters/Saudi Civil Defense), Hormuz/oil (Reuters), Australia (Reuters),
Hasina (Reuters), Sarkozy/Zelenskiy (Reuters), UNAIDS (unaids.org).
Dropped as unverifiable: the IRGC "three tankers hit mines" claim (Reuters
could not verify it) and the "Indonesia VP resigns" item (that was 12 Nov).
"""

import hashlib
import os
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 30
CW = W - 2 * MARGIN  # 964

PAPER = (251, 249, 242)
INK = (20, 20, 20)
MUTED = (85, 85, 85)
ACCENT = (140, 29, 24)      # dark red for kickers
RULE = (20, 20, 20)
BAR = (36, 66, 92)          # steel blue for chart bars
BAR_HL = (140, 29, 24)      # NVDA bar in accent red

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
LIB_DIR = "/usr/share/fonts/truetype/liberation"


def font(name, size, base=FONT_DIR):
    return ImageFont.truetype(os.path.join(base, name), size)


F_SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
F_SERIF = lambda s: font("DejaVuSerif.ttf", s)
F_SERIF_I = lambda s: font("LiberationSerif-Italic.ttf", s, LIB_DIR)
F_SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
F_SANS = lambda s: font("DejaVuSans.ttf", s)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap by pixel width. Returns a list of lines."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(draw, x, y, text, fnt, max_w, leading, color=INK):
    """Draw wrapped paragraph; return y after the last line."""
    for line in wrap(draw, text, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=color)
        y += leading
    return y


def draw_kicker(draw, x, y, text, fnt):
    draw.text((x, y), text, font=fnt, fill=ACCENT)
    return y + int(fnt.size * 1.5)


def hrule(draw, y, x0=MARGIN, x1=W - MARGIN, width=1):
    draw.line([(x0, y), (x1, y)], fill=RULE, width=width)
    return y + width


def vrule(draw, x, y0, y1, width=1):
    draw.line([(x, y0), (x, y1)], fill=(150, 150, 150), width=width)


def draw_chart(draw, x, y, w):
    """Horizontal bar chart of Tuesday's market moves. Returns bottom y."""
    title = F_SANS_B(14)
    draw.text((x, y), "TUESDAY'S MARKET REVERSAL", font=title, fill=INK)
    y += 26
    label_f = F_SANS_B(15)
    val_f = F_SANS_B(15)
    rows = [
        ("NVDA", -6.0, BAR_HL),
        ("NASDAQ", -1.5, BAR),
        ("S&P 500", -0.5, BAR),
        ("DOW", 0.9, BAR),
    ]
    bar_max = w - 152  # label (78) + gap + value text, so nothing clips right
    scale = bar_max / 6.0
    for name, val, color in rows:
        draw.text((x, y), name, font=label_f, fill=INK)
        bx = x + 78
        bw = max(4, int(abs(val) * scale))
        draw.rectangle([bx, y + 2, bx + bw, y + 22], fill=color)
        sign = "+" if val >= 0 else ""
        draw.text((bx + bw + 8, y), "%s%.1f%%" % (sign, val),
                  font=val_f, fill=INK)
        y += 34
    foot = F_SANS(12)
    y += 2
    y = draw_para(draw, x, y,
                  "One-day change, Tuesday 24 Nov 2026. Sources: Reuters.",
                  foot, w, 16, color=MUTED)
    return y


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Outer double border.
    d.rectangle([10, 10, W - 11, H - 11], outline=RULE, width=2)
    d.rectangle([16, 16, W - 17, H - 17], outline=RULE, width=1)

    y = 32
    # Dateline row.
    dl = F_SANS_B(14)
    d.text((MARGIN, y), "WEDNESDAY, 25 NOVEMBER 2026", font=dl, fill=INK)
    right = "ONE PAGE · SIX STORIES"
    d.text((W - MARGIN - d.textlength(right, font=dl), y), right,
           font=dl, fill=INK)
    y += 26

    # Masthead.
    mast = F_SERIF_B(56)
    name = "THE DAILY DISPATCH"
    d.text(((W - d.textlength(name, font=mast)) / 2, y), name,
           font=mast, fill=INK)
    y += 70

    # Tagline.
    tag = F_SERIF_I(16)
    tagline = ("A Pakistani flies to China's space station, Wall Street's "
               "AI rally fades, and a drone hits Riyadh.")
    d.text(((W - d.textlength(tagline, font=tag)) / 2, y), tagline,
           font=tag, fill=MUTED)
    y += 28
    y = hrule(d, y, width=3)
    y = hrule(d, y + 3, width=1)
    y += 10

    # ---- Lead story: Shenzhou-24 ----
    lead_x, lead_w = MARGIN, 620
    chart_x, chart_w = 680, W - MARGIN - 680
    ly = y
    ly = draw_kicker(d, lead_x, ly, "SPACE · LEAD STORY", F_SANS_B(15))
    ly = draw_para(d, lead_x, ly,
                   "Pakistan reaches orbit on Shenzhou-24",
                   F_SERIF_B(36), lead_w, 44)
    ly += 6
    ly = draw_para(d, lead_x, ly,
                   "Muhammad Zeeshan Ali becomes the first Pakistani in "
                   "space — and the first foreign astronaut aboard China's "
                   "station.",
                   F_SERIF_I(18), lead_w, 24)
    ly += 6
    ly = draw_para(d, lead_x, ly,
                   "China launched the Shenzhou-24 crewed spaceship on "
                   "Wednesday, sending three astronauts to its Tiangong "
                   "station aboard a Long March-2F rocket. Commander Tang "
                   "Hongbo and flight engineer Wu Yi fly with Ali, 40, a "
                   "Pakistan Air Force pilot who will work as a payload "
                   "specialist for five to ten days, running four Pakistani "
                   "biotech experiments.",
                   F_SERIF(16), lead_w, 20)
    chart_bottom = draw_chart(d, chart_x, y + 4, chart_w)
    y = max(ly, chart_bottom) + 8
    print("  after lead: y =", y)
    y = hrule(d, y, width=1)
    y += 8

    # ---- Row 2: two columns ----
    col_w = (CW - 20) // 2
    row2_top = y
    y2 = []
    stories2 = [
        (MARGIN, "MARKETS · THE REVERSAL",
         "Nvidia's bounce fades a day after its 31% surge",
         "Nvidia fell 6% on Tuesday and the Nasdaq lost 1.5% as the relief "
         "rally around Jensen Huang's return fizzled. Selling worsened on a "
         "report of new US tariffs on China, the EU and 14 other economies; "
         "Anthropic slid below its $83 IPO price."),
        (MARGIN + col_w + 20, "RIYADH · DRONE STRIKE",
         "Houthi drone hits Riyadh's tallest tower, 11 hurt",
         "A Houthi drone struck a tower in Riyadh's financial district on "
         "Tuesday, wounding 11 people, Saudi Civil Defense said. It was the "
         "second strike on the district in under a week; the Saudi-led "
         "coalition vowed a decisive response."),
    ]
    for x, kick, head, body in stories2:
        cy = row2_top
        cy = draw_kicker(d, x, cy, kick, F_SANS_B(14))
        cy = draw_para(d, x, cy, head, F_SERIF_B(28), col_w, 35)
        cy += 4
        cy = draw_para(d, x, cy, body, F_SERIF(16), col_w, 20)
        y2.append(cy)
    vrule(d, MARGIN + col_w + 10, row2_top + 2, max(y2) - 4)
    y = max(y2) + 8
    print("  after row2: y =", y)
    y = hrule(d, y, width=1)
    y += 8

    # ---- Row 3: three columns ----
    col3_w = (CW - 40) // 3
    row3_top = y
    y3 = []
    stories3 = [
        (MARGIN, "THE GULF",
         "Iran vows to fight US blockade as oil slips",
         "Iran will use \u201call available means\u201d against the US naval "
         "blockade, its foreign ministry said. Brent fell 0.5% to $90.97 "
         "on Wednesday; OPEC+ meets on 29 November."),
        (MARGIN + col3_w + 20, "AUSTRALIA",
         "Canberra apologises to LGBTQ veterans",
         "Australia formally apologised on Wednesday to current and former "
         "LGBTQ service members for decades of discriminatory policies. "
         "Defence Minister Richard Marles delivered the apology in "
         "parliament."),
        (MARGIN + 2 * (col3_w + 20), "BANGLADESH",
         "Hasina plans return home on 16 December",
         "Ousted PM Sheikh Hasina plans to fly home from exile in India on "
         "16 December, her spokesperson told Reuters. A minister said she "
         "would be arrested; she faces a death sentence over the 2024 "
         "crackdown."),
    ]
    for i, (x, kick, head, body) in enumerate(stories3):
        cy = row3_top
        cy = draw_kicker(d, x, cy, kick, F_SANS_B(13))
        cy = draw_para(d, x, cy, head, F_SERIF_B(23), col3_w, 28)
        cy += 4
        cy = draw_para(d, x, cy, body, F_SERIF(15), col3_w, 18)
        y3.append(cy)
    # Dividers after the loop, so both span the full column height.
    vrule(d, MARGIN + col3_w + 10, row3_top + 2, max(y3) - 4)
    vrule(d, MARGIN + 2 * col3_w + 30, row3_top + 2, max(y3) - 4)
    y = max(y3) + 8
    print("  after row3: y =", y)
    y = hrule(d, y, width=1)
    y += 8

    # ---- In brief ----
    y = draw_kicker(d, MARGIN, y, "IN BRIEF", F_SANS_B(14))
    briefs = [
        ("FRANCE — ", "Sarkozy and wife Carla Bruni were ordered to trial "
         "in a corruption case; a first hearing is set for 1 April 2027."),
        ("BALTIC — ", "Zelensky confirmed Ukraine's drone strike on a "
         "Russian cargo ship in the Gulf of Finland; Norway urged caution."),
        ("HEALTH — ", "AIDS deaths fell to 570,000 in 2025, the lowest in "
         "20+ years, but HIV funding fell 18%, UNAIDS said."),
    ]
    # Three briefs side by side, all starting at the same top y.
    by = y
    for i, (lead, text) in enumerate(briefs):
        bx = MARGIN + i * (col3_w + 20)
        bold = F_SERIF_B(14)
        reg = F_SERIF(14)
        full = lead + text
        lines = wrap(d, full, reg, col3_w)
        yy = y
        for li, line in enumerate(lines):
            if li == 0:
                d.text((bx, yy), lead, font=bold, fill=INK)
                d.text((bx + d.textlength(lead, font=bold), yy),
                       line[len(lead):], font=reg, fill=INK)
            else:
                d.text((bx, yy), line, font=reg, fill=INK)
            yy += 17
        by = max(by, yy)
    y = by + 6
    print("  after briefs: y =", y)
    y = hrule(d, y, width=1)
    y += 6

    # Footer.
    foot = F_SANS(12)
    left = ("Sources: Reuters, Xinhua, China Manned Space Agency, Saudi "
            "Civil Defense, UNAIDS")
    d.text((MARGIN, y), left, font=foot, fill=MUTED)
    right = "Wednesday, 25 November 2026"
    d.text((W - MARGIN - d.textlength(right, font=foot), y), right,
           font=foot, fill=MUTED)
    y += 18

    print("layout: final y =", y, "of", H, "| bottom margin =", H - 18 - y)
    if y > H - 18:
        print("WARNING: content overflows the page", file=sys.stderr)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG", optimize=True)
    data = open(out, "rb").read()
    print("wrote", out, "| bytes:", len(data),
          "| sha256:", hashlib.sha256(data).hexdigest())
    assert len(data) <= 1048576, "entry.png exceeds 1 MiB"
    assert img.size == (1024, 1024)


if __name__ == "__main__":
    main()
