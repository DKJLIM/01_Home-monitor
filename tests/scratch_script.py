#test of current script 
import sys
import os
import time
import traceback

from pathlib import Path
from PIL import Image # to change photos
from PIL import Image,ImageDraw,ImageFont

#setting local paths
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'assets/pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'assets/lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

# import local libraries/modules
import logging
from waveshare_epd import epd7in5_V2_old # specific set of modules from waveshare

sys.path.append(str(Path(__file__).parent.parent / 'src' / 'modules'))
from src.modules import printing_image as pim

# ACTUAL SCRIPTS
logging.basicConfig(level=logging.DEBUG)

# Displaying a simple image
epd = epd7in5_V2_old.EPD()
screen_render = pim.ScreenRender(epd = epd, 
                                 picdir = picdir, 
                                 libdir=libdir)


# clear screen
screen_render.screen_clear()

# render image
filepath_image = Image.open(os.path.join(picdir, 'test.bmp'))
screen_render.screen_render_image(filepath_image=filepath_image)
print('end')