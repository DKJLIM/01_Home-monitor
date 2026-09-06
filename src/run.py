#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
run.py
------
Main entry point for the home monitor.
Renders the dashboard to the e-ink display and refreshes every 60 seconds,
using a fast partial refresh. Every 10 minutes (FULL_REFRESH_EVERY cycles) it
instead does a full refresh, which clears the ghosting partial refreshes
leave behind over time.

Usage:
    python src/run.py            # run forever, driving the physical display
    python src/run.py --preview  # render once, save dashboard_preview.png, exit

Stop with Ctrl+C — the display will be put to sleep cleanly.
"""

import logging
import sys
import time
from pathlib import Path

from PIL import ImageDraw

sys.path.insert(0, str(Path(__file__).parent / "modules"))

from screen_renderer import ScreenRenderer, DISPLAY_WIDTH, DISPLAY_HEIGHT
from tfl_client import TflClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)

REFRESH_INTERVAL = 60  # seconds between display updates
FULL_REFRESH_EVERY = 10  # cycles (~10 min) — periodic full refresh clears e-ink ghosting

# ── Layout constants ───────────────────────────────────────────────────────────
BLACK      = 0
WHITE      = 255
LIGHT_GREY = 200
MID_GREY   = 120

PADDING  = 15
ROW_H    = 40
HEADER_H = 110
FOOTER_H = 28

COL_DEST = PADDING
COL_LINE = 220
COL_PLAT = 350
COL_MINS = 730


def draw_header(draw, font_clock, font_date):
    draw.rectangle([(0, 0), (DISPLAY_WIDTH, HEADER_H)], fill=BLACK)
    now      = time.localtime()
    time_str = time.strftime("%H:%M:%S", now)
    date_str = time.strftime("%A  %d %B %Y", now)
    draw.text((PADDING, 10), time_str, font=font_clock, fill=WHITE)
    date_w = draw.textlength(date_str, font=font_date)
    draw.text((DISPLAY_WIDTH - PADDING - date_w, HEADER_H - 40), date_str,
              font=font_date, fill=WHITE)


def draw_trains(draw, arrivals, font_section, font_label, font_row, start_y):
    y = start_y
    draw.text((PADDING, y), "Canning Town  —  Upcoming Trains",
              font=font_section, fill=BLACK)
    y += 36

    draw.line([(PADDING, y), (DISPLAY_WIDTH - PADDING, y)], fill=BLACK, width=2)
    y += 6

    draw.text((COL_DEST, y), "Destination", font=font_label, fill=MID_GREY)
    draw.text((COL_LINE, y), "Line",        font=font_label, fill=MID_GREY)
    draw.text((COL_PLAT, y), "Platform",    font=font_label, fill=MID_GREY)
    draw.text((COL_MINS, y), "Min",         font=font_label, fill=MID_GREY)
    y += 20

    draw.line([(PADDING, y), (DISPLAY_WIDTH - PADDING, y)], fill=LIGHT_GREY, width=1)
    y += 4

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


def draw_footer(draw, font_label):
    footer_y = DISPLAY_HEIGHT - FOOTER_H
    draw.line([(0, footer_y - 4), (DISPLAY_WIDTH, footer_y - 4)], fill=BLACK, width=1)
    draw.text((PADDING, footer_y), f"Updated: {time.strftime('%H:%M:%S')}",
              font=font_label, fill=MID_GREY)


def render_once(renderer, tfl, fonts, save_preview=None, full=False):
    font_clock, font_date, font_section, font_row, font_label = fonts

    logging.info("Fetching TfL arrivals…")
    arrivals = tfl.get_arrivals()
    logging.info("Got %d arrivals", len(arrivals))

    img  = renderer.new_canvas()
    draw = ImageDraw.Draw(img)

    draw_header(draw, font_clock, font_date)
    draw_trains(draw, arrivals, font_section, font_label, font_row, start_y=HEADER_H + 12)
    draw_footer(draw, font_label)

    renderer.render(img, save_preview=save_preview, full=full)


def main(preview_only=False):
    renderer = ScreenRenderer(preview_mode=preview_only)
    tfl      = TflClient()

    # Load fonts once — reused every iteration
    fonts = (
        renderer.get_font(80),   # clock
        renderer.get_font(32),   # date
        renderer.get_font(20),   # section heading
        renderer.get_font(20),   # table rows
        renderer.get_font(16),   # labels / footer
    )

    if preview_only:
        preview_path = str(Path(__file__).parent.parent / "dashboard_preview.png")
        render_once(renderer, tfl, fonts, save_preview=preview_path)
        return

    logging.info("Initialising display")
    renderer.init()
    renderer.clear()

    cycle = 0
    try:
        while True:
            cycle += 1
            try:
                full_refresh = (cycle % FULL_REFRESH_EVERY == 0)
                render_once(renderer, tfl, fonts, full=full_refresh)
            except Exception as exc:
                # Log the error but keep the loop running
                logging.error("Render error (will retry next cycle): %s", exc)

            logging.info("Sleeping %ds until next refresh…", REFRESH_INTERVAL)
            time.sleep(REFRESH_INTERVAL)

    except KeyboardInterrupt:
        logging.info("Interrupted — putting display to sleep")
        renderer.sleep()
        try:
            from waveshare_epd import epd7in5_V2
            epd7in5_V2.epdconfig.module_exit(cleanup=True)
        except Exception:
            pass


if __name__ == "__main__":
    main(preview_only="--preview" in sys.argv)
