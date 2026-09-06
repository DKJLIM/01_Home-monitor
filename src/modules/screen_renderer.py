#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
screen_renderer.py
------------------
Dedicated module for rendering images to the WaveShare epd7in5_V2 e-ink display.
Supports a preview_mode flag so the dashboard can be developed and tested
without physical hardware (saves a PNG instead of driving the display).
"""

import logging
import sys
from pathlib import Path
from PIL import Image, ImageFont

PICDIR = Path(__file__).parent.parent / "assets" / "pic"
LIBDIR = Path(__file__).parent.parent / "assets" / "lib"

DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 480


class ScreenRenderer:
    """Renders PIL images to the WaveShare 7.5" V2 e-ink display."""

    def __init__(self, preview_mode: bool = False):
        """
        Args:
            preview_mode: When True the display hardware is not initialised;
                          render() only saves a PNG preview file.
        """
        self.preview_mode = preview_mode
        self.epd = None

        if not preview_mode:
            if LIBDIR.exists():
                sys.path.append(str(LIBDIR))
            try:
                from waveshare_epd import epd7in5_V2  # noqa: PLC0415
                self.epd = epd7in5_V2.EPD()
                logging.info("WaveShare epd7in5_V2 driver loaded")
            except (ImportError, OSError, Exception) as exc:
                logging.warning(
                    "WaveShare library not available — falling back to preview mode: %s", exc
                )
                self.preview_mode = True

    # ------------------------------------------------------------------
    # Display lifecycle
    # ------------------------------------------------------------------

    def init(self) -> None:
        """Initialise the display."""
        if not self.preview_mode:
            logging.info("Initialising display")
            self.epd.init_part()

    def clear(self) -> None:
        """Clear the display to white."""
        if not self.preview_mode:
            logging.info("Clearing display")
            self.epd.Clear()

    def sleep(self) -> None:
        """Put the display into low-power sleep mode."""
        if not self.preview_mode:
            logging.info("Display going to sleep")
            self.epd.sleep()

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def render(self, image: Image.Image, save_preview: str = None, full: bool = False) -> None:
        """
        Send a PIL Image to the display.

        Args:
            image: PIL Image (mode 'L', size 800×480).
            save_preview: Optional filesystem path; if given, the image is
                          also saved as a PNG (useful for debugging).
            full: When True, do a full-quality refresh (init + Clear +
                  display) instead of the fast partial refresh. Partial
                  refreshes accumulate visible ghosting over time, so this
                  should be used periodically to clear it.
        """
        if save_preview:
            image.save(save_preview)
            logging.info("Preview saved to %s", save_preview)

        if not self.preview_mode:
            if full:
                logging.info("Performing full refresh (clears ghosting)")
                self.epd.init()
                self.epd.Clear()
                self.epd.display(self.epd.getbuffer(image))
                self.epd.init_part()
            else:
                self.epd.display_Partial(self.epd.getbuffer(image), 0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT)
            logging.info("Image rendered to display")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Return a TrueType font at the requested point size."""
        font_path = PICDIR / "Font.ttc"
        return ImageFont.truetype(str(font_path), size)

    def new_canvas(self) -> Image.Image:
        """Return a blank white 800×480 grayscale canvas."""
        return Image.new("L", (DISPLAY_WIDTH, DISPLAY_HEIGHT), 255)
