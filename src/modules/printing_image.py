#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
from PIL import Image # to change photos


import logging
from waveshare_epd import epd7in5_V2_old
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

from pathlib import Path

# Go up two levels, then into assets/pic
picdir = Path(__file__).parent.parent.parent / 'assets' / 'pic'
libdir = Path(__file__).parent.parent.parent / 'assets' / 'lib'

class ScreenRender:
    def __init__(self, epd, picdir, libdir):
        """
        Initializes the screen rendering class.
        params(s):
            epd: instance of the e-paper display class
            picdir: directory where images are stored
            libdir: directory where libraries are stored
        """
        self.epd = epd
        self.picdir = picdir
        self.libdir = libdir

    def screen_clear(self):
        """clean display."""
        logging.info("Clear screen")
        self.epd.init()
        self.epd.Clear()

    def screen_render_image(self, filepath_image):
        """        Renders an image on the e-paper display.
        :param(s):
            image: filepath to image
        """
        logging.info("rendering image to display")
        self.epd.display(self.epd.getbuffer(filepath_image))

class image_processor:
    def __init__(self):
        """
        this class is to process images before rendering.
        """
        self.image_raw = None
        self.image_processed = None
    
    def image_process(self):
        #some steps to process image 
        # convert to grayscale 
        # convert to BMP 
        # convert to maximum resolution
        print('hi')

    def image_resize(self):
        # reside image to make it smaller
        print('hi')


