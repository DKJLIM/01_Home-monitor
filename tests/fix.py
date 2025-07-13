#test of current script 
import sys
import os
import time
import traceback

from pathlib import Path
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


####################################################
# ACTUAL SCRIPTS

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
    epd = epd7in5_V2_old.EPD()
    print("Initializing display...")
    epd.init()


    # Create a simple test image
    image = Image.new('1', (epd.width, epd.height), 255) # White background
    draw = ImageDraw.Draw(image)
    draw.rectangle((0,0, 800, 480), fill=0, outline = 0) # Black rectangle
    

    draw.rectangle((10, 10, 700, 350), fill= 20, outline = 1) # Black rectangle
    draw.text((10, 10), "Hello, Waveshare EPD!", font=get_font(24), fill=0) # Black text
    
   
    
    print("Displaying test image...")
    epd.display(epd.getbuffer(image))
    time.sleep(5) # Wait for refresh
    
    print("Clearing display...")
    epd.reset()
    epd.Clear()
    time.sleep(5)
    epd.sleep()
    print("Done")
except Exception as e:
    print(f"Error: {e}")