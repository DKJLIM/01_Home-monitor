#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
test_dashboard_render.py
------------------------
Renders the home monitor dashboard to the e-ink display using the
screen_renderer and tfl_client modules.

On a Raspberry Pi (with display connected):
    python src/test/test_dashboard_render.py

Off-Pi / preview mode (saves dashboard_preview.png, no hardware needed):
    python src/test/test_dashboard_render.py --preview
"""

import logging
import math
import sys
import time
import traceback
from pathlib import Path

from PIL import Image, ImageDraw

# ── Path setup ─────────────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent.parent / "modules"))

from screen_renderer import ScreenRenderer, DISPLAY_WIDTH, DISPLAY_HEIGHT
from tfl_client import TflClient

logging.basicConfig(level=logging.DEBUG)

PREVIEW_PATH = Path(__file__).parent.parent.parent / "dashboard_preview.png"

# ── Colours ────────────────────────────────────────────────────────────────────
BLACK      = 0
WHITE      = 255
LIGHT_GREY = 200
MID_GREY   = 120

# ── Layout ─────────────────────────────────────────────────────────────────────
PADDING    = 15
ROW_H      = 40

COL_DEST   = PADDING
COL_LINE   = 220
COL_PLAT   = 350
COL_MINS   = 730

HEADER_H   = 110
FOOTER_H   = 28


def draw_header(draw, font_clock, font_date):
    """Black header bar with time (large) and date (right-aligned)."""
    draw.rectangle([(0, 0), (DISPLAY_WIDTH, HEADER_H)], fill=BLACK)

    now = time.localtime()
    time_str = time.strftime("%H:%M", now)
    date_str = time.strftime("%A  %d %B %Y", now)

    draw.text((PADDING, 10), time_str, font=font_clock, fill=WHITE)

    date_w = draw.textlength(date_str, font=font_date)
    draw.text((DISPLAY_WIDTH - PADDING - date_w, HEADER_H - 40), date_str,
              font=font_date, fill=WHITE)


def draw_trains(draw, arrivals, font_section, font_label, font_row, start_y):
    """Arrivals table starting at start_y; returns the y position after the last row."""
    y = start_y

    draw.text((PADDING, y), "Canning Town  —  Upcoming Trains",
              font=font_section, fill=BLACK)
    y += 36

    draw.line([(PADDING, y), (DISPLAY_WIDTH - PADDING, y)], fill=BLACK, width=2)
    y += 6

    # Column headers
    draw.text((COL_DEST, y), "Destination", font=font_label, fill=MID_GREY)
    draw.text((COL_LINE, y), "Line",        font=font_label, fill=MID_GREY)
    draw.text((COL_PLAT, y), "Platform",    font=font_label, fill=MID_GREY)
    draw.text((COL_MINS, y), "Min",         font=font_label, fill=MID_GREY)
    y += 20

    draw.line([(PADDING, y), (DISPLAY_WIDTH - PADDING, y)], fill=LIGHT_GREY, width=1)
    y += 4

    # How many rows fit above the footer
    max_rows = (DISPLAY_HEIGHT - FOOTER_H - y) // ROW_H
    visible  = arrivals[:max_rows]

    for i, arrival in enumerate(visible):
        bg = LIGHT_GREY if i % 2 == 0 else WHITE
        draw.rectangle([(PADDING, y), (DISPLAY_WIDTH - PADDING, y + ROW_H - 2)], fill=bg)

        dest = (arrival.destination
                .replace(" Underground Station", "")
                .replace(" DLR Station", "")
                .replace(" Rail Station", ""))

        mins_label = "Due" if arrival.minutes_away == 0 else str(arrival.minutes_away)

        draw.text((COL_DEST, y + 6), dest,              font=font_row, fill=BLACK)
        draw.text((COL_LINE, y + 6), arrival.line_name, font=font_row, fill=BLACK)
        draw.text((COL_PLAT, y + 6), arrival.platform,  font=font_row, fill=BLACK)
        draw.text((COL_MINS, y + 6), mins_label,        font=font_row, fill=BLACK)
        y += ROW_H

    if not visible:
        draw.text((PADDING, y + 8), "No live data available.", font=font_row, fill=MID_GREY)

    return y


def draw_footer(draw, font_label):
    footer_y = DISPLAY_HEIGHT - FOOTER_H
    draw.line([(0, footer_y - 4), (DISPLAY_WIDTH, footer_y - 4)], fill=BLACK, width=1)
    updated = f"Updated: {time.strftime('%H:%M:%S')}"
    draw.text((PADDING, footer_y), updated, font=font_label, fill=MID_GREY)


# ── Main ───────────────────────────────────────────────────────────────────────

preview_mode = "--preview" in sys.argv

try:
    logging.info("Initialising renderer")
    renderer = ScreenRenderer(preview_mode=preview_mode)

    logging.info("Fetching TfL arrivals")
    tfl      = TflClient()
    arrivals = tfl.get_arrivals()
    logging.info("Got %d arrivals", len(arrivals))

    # ── Build image ─────────────────────────────────────────────────────────────
    logging.info("Building dashboard image")
    img  = renderer.new_canvas()
    draw = ImageDraw.Draw(img)

    font_clock   = renderer.get_font(80)
    font_date    = renderer.get_font(32)
    font_section = renderer.get_font(20)
    font_row     = renderer.get_font(20)
    font_label   = renderer.get_font(16)

    draw_header(draw, font_clock, font_date)
    draw_trains(draw, arrivals, font_section, font_label, font_row, start_y=HEADER_H + 12)
    draw_footer(draw, font_label)

    # ── Send to display ─────────────────────────────────────────────────────────
    if not preview_mode:
        logging.info("init and Clear")
        renderer.init()
        renderer.clear()

    renderer.render(img, save_preview=str(PREVIEW_PATH))
    logging.info("Preview saved: %s", PREVIEW_PATH)

    if not preview_mode:
        time.sleep(2)
        logging.info("Goto Sleep...")
        renderer.sleep()

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c — exiting")
    if not preview_mode:
        # clean up GPIO if on Pi
        try:
            from waveshare_epd import epd7in5_V2
            epd7in5_V2.epdconfig.module_exit(cleanup=True)
        except Exception:
            pass
    exit()
