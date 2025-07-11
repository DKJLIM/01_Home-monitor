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

set_of_fonts = {}
for size in range(12, 200, 2):
    set_of_fonts[size] = get_font(size)

try:   
    epd.init()
    epd.Clear()

    # Generate a list of fonts with different sizes
    logging.info("Drawing Weather Dashboard...")

    # Create new image (assuming similar dimensions to your setup)
    Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    print('EPD size:', epd.width,":",epd.height)
    draw = ImageDraw.Draw(Himage)

    # Weather Dashboard Title
    draw.text(xy = (10, 5), text = 'DO NOT SUCK THE PENIS', font=set_of_fonts[70], fill=0)
    draw.line((10, 80, 700, 80), fill=0)  # Underline

    # include an image below the title
    weather_image_path = os.path.join(picdir, 'test.bmp')  # Path to your weather icon
    if os.path.exists(weather_image_path):
        weather_icon = Image.open(weather_image_path)
        weather_icon = weather_icon.resize((100, 100), Image.ANTIALIAS)  # Resize if necessary
        Himage.paste(weather_icon, (10, 90))  # Paste the icon at position (10, 90)

    

    # Display the image
    epd.display(epd.getbuffer(Himage))
    time.sleep(2)

    logging.info("Goto Sleep...")
    epd.sleep()

except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd7in5_V2_old.epdconfig.module_exit(cleanup=True)
    exit()
