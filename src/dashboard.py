#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
dashboard.py
------------
Builds and renders the home-monitor dashboard image.

Layout (800 × 480 px):
    ┌──────────────────────────────────────────────────────────┐
    │  HH:MM          Day  DD Month YYYY              [header] │
    ├──────────────────────────────────────────────────────────┤
    │  Canning Town — Upcoming Trains                          │
    │  Destination          Line      Platform    Mins         │
    │  ───────────────────────────────────────────────────     │
    │  Stratford            DLR       Eastbound    2           │
    │  Bank                 DLR       Westbound    4           │
    │  ...                                                     │
    ├──────────────────────────────────────────────────────────┤
    │  Updated: HH:MM:SS                              [footer] │
    └──────────────────────────────────────────────────────────┘

Run with --preview to generate a PNG without display hardware:
    python src/dashboard.py --preview
"""

import logging
import sys
import time
from pathlib import Path
from typing import List

from PIL import Image, ImageDraw

# Allow imports from src/modules whether running from project root or src/
sys.path.insert(0, str(Path(__file__).parent / "modules"))

from screen_renderer import ScreenRenderer, DISPLAY_WIDTH, DISPLAY_HEIGHT  # noqa: E402
from tfl_client import TflClient, Arrival  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)

# ── Output path for PNG preview ────────────────────────────────────────────────
PREVIEW_PATH = Path(__file__).parent.parent / "dashboard_preview.png"

# ── Layout constants ───────────────────────────────────────────────────────────
PADDING = 15
ROW_HEIGHT = 40

# Greyscale colour values (0 = black, 255 = white)
BLACK = 0
WHITE = 255
LIGHT_GREY = 200
MID_GREY = 120

# Column x-positions for the arrivals table
COL_DEST = PADDING
COL_LINE = 420
COL_PLAT = 580
COL_MINS = 730


# ── Dashboard builder ──────────────────────────────────────────────────────────

def build_dashboard(renderer: ScreenRenderer, arrivals: List[Arrival]) -> Image.Image:
    """Compose and return an 800×480 greyscale dashboard image."""
    img = renderer.new_canvas()
    draw = ImageDraw.Draw(img)

    font_clock = renderer.get_font(80)
    font_date = renderer.get_font(32)
    font_section = renderer.get_font(28)
    font_row = renderer.get_font(26)
    font_label = renderer.get_font(20)

    now = time.localtime()

    # ── Header bar ─────────────────────────────────────────────────────────────
    HEADER_H = 110
    draw.rectangle([(0, 0), (DISPLAY_WIDTH, HEADER_H)], fill=BLACK)

    time_str = time.strftime("%H:%M", now)
    date_str = time.strftime("%A  %d %B %Y", now)

    draw.text((PADDING, 10), time_str, font=font_clock, fill=WHITE)
    # Right-align the date in the header
    date_w = draw.textlength(date_str, font=font_date)
    draw.text((DISPLAY_WIDTH - PADDING - date_w, HEADER_H - 40), date_str, font=font_date, fill=WHITE)

    # ── Train section ───────────────────────────────────────────────────────────
    y = HEADER_H + 12
    draw.text((PADDING, y), "Canning Town  —  Upcoming Trains", font=font_section, fill=BLACK)
    y += 36

    # Divider
    draw.line([(PADDING, y), (DISPLAY_WIDTH - PADDING, y)], fill=BLACK, width=2)
    y += 6

    # Column headers
    draw.text((COL_DEST, y), "Destination", font=font_label, fill=MID_GREY)
    draw.text((COL_LINE, y), "Line", font=font_label, fill=MID_GREY)
    draw.text((COL_PLAT, y), "Platform", font=font_label, fill=MID_GREY)
    draw.text((COL_MINS, y), "Min", font=font_label, fill=MID_GREY)
    y += 22

    draw.line([(PADDING, y), (DISPLAY_WIDTH - PADDING, y)], fill=LIGHT_GREY, width=1)
    y += 4

    # Arrival rows — alternate background for readability
    max_rows = (DISPLAY_HEIGHT - y - 32) // ROW_HEIGHT
    visible = arrivals[:max_rows] if arrivals else []

    for i, arrival in enumerate(visible):
        row_bg = LIGHT_GREY if i % 2 == 0 else WHITE
        draw.rectangle(
            [(PADDING, y), (DISPLAY_WIDTH - PADDING, y + ROW_HEIGHT - 2)],
            fill=row_bg,
        )

        # Tidy up long station names
        dest = (
            arrival.destination
            .replace(" Underground Station", "")
            .replace(" DLR Station", "")
            .replace(" Rail Station", "")
        )

        mins_label = "Due" if arrival.minutes_away == 0 else str(arrival.minutes_away)

        draw.text((COL_DEST, y + 6), dest, font=font_row, fill=BLACK)
        draw.text((COL_LINE, y + 6), arrival.line_name, font=font_row, fill=BLACK)
        draw.text((COL_PLAT, y + 6), arrival.platform, font=font_row, fill=BLACK)
        draw.text((COL_MINS, y + 6), mins_label, font=font_row, fill=BLACK)

        y += ROW_HEIGHT

    if not visible:
        draw.text(
            (PADDING, y + 8),
            "No live train data available.",
            font=font_row,
            fill=MID_GREY,
        )

    # ── Footer ──────────────────────────────────────────────────────────────────
    footer_y = DISPLAY_HEIGHT - 28
    draw.line([(0, footer_y - 4), (DISPLAY_WIDTH, footer_y - 4)], fill=BLACK, width=1)
    updated = f"Updated: {time.strftime('%H:%M:%S', now)}"
    draw.text((PADDING, footer_y), updated, font=font_label, fill=MID_GREY)

    return img


# ── Entry point ────────────────────────────────────────────────────────────────

def main(preview_only: bool = False) -> None:
    renderer = ScreenRenderer(preview_mode=preview_only)
    tfl = TflClient()

    logging.info("Fetching TfL arrivals at Canning Town…")
    arrivals = tfl.get_arrivals()
    logging.info("Received %d arrivals", len(arrivals))
    for a in arrivals:
        logging.info("  %s", a)

    logging.info("Building dashboard…")
    img = build_dashboard(renderer, arrivals)

    if not preview_only:
        renderer.init()
        renderer.clear()

    renderer.render(img, save_preview=str(PREVIEW_PATH))

    if not preview_only:
        renderer.sleep()

    logging.info("Dashboard complete. Preview at: %s", PREVIEW_PATH)


if __name__ == "__main__":
    main(preview_only="--preview" in sys.argv)
