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
# from waveshare_epd import epd7in5_V2 # specific set of modules from waveshare

sys.path.append(str(Path(__file__).parent.parent))
from src.modules import printing_image as pim

# ACTUAL SCRIPTS
logging.basicConfig(level=logging.DEBUG)

logging.info("epd7in5_V2 Demo")
epd = epd7in5_V2_old.EPD()
logging.info("init and Clear")

def get_font(size):
    """
    Returns a font object with the specified size.
    :param size: Size of the font
    :return: Font object
    """
    return ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), size)



epd.init()
epd.Clear()

# Generate a list of fonts with different sizes
logging.info("Drawing Weather Dashboard...")

# Create new image (assuming similar dimensions to your setup)
Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
print('EPD size:', epd.width,":",epd.height)
draw = ImageDraw.Draw(Himage)

set_of_fonts = {}
for size in range(12, 200, 2):
    set_of_fonts[size] = get_font(size)



def draw_box(size, position): 
    draw = ImageDraw.Draw(Himage)
    coords_1 = (position[0], position[1])
    coords_2 = (position[0] + size[0], position[1] + size[1])
    draw.rectangle((coords_1, coords_2),
                    fill=1,
                    outline=0)  # Draw a white box with black outline

draw_box((100, 100), (10, 10))  # Example usage of draw_box function
# Display the image
epd.display(epd.getbuffer(Himage))
time.sleep(2)