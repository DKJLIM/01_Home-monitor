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
from waveshare_epd import epd7in5_V2 # specific set of modules from waveshare

sys.path.append(str(Path(__file__).parent.parent))
from src.modules import printing_image as pim

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

class dashboard_widget:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.image = None

class dashboard_planner:
    def __init__(self):
        self.row_columns = list()
        self.coordinates_list = list()
    
    # def calculate_coordinates(self):

    #     coordinates_results = .... 
        
    #     self.coordinates = coordinates_results

def draw_box(size, position): 
    draw = ImageDraw.Draw(Himage)
    coords_1 = (position[0], position[1])
    coords_2 = (position[0] + size[0], position[1] + size[1])
    draw.rectangle((coords_1, coords_2),
                    fill=1,
                    outline=0)  # Draw a white box with black outline


logging.basicConfig(level=logging.DEBUG)



# epd.Clear()

try:   
    logging.info("epd7in5_V2 Demo")
    epd = epd7in5_V2_old.EPD()

    logging.info("init and Clear")
    epd.init()
    epd.Clear()

    #pseudo fix at the moment
    # image = Image.new('1', (epd.width, epd.height), 1) # White background
    # draw = ImageDraw.Draw(image)
    # draw.rectangle((0,0, 800, 480), fill=1, outline = 1) # White background

    # Generate a list of fonts with different sizes
    logging.info("Drawing Weather Dashboard...")

    # # Create new image (assuming similar dimensions to your setup)
    Himage = Image.new(mode = 'L', size = (epd.width, epd.height), color = 1)  # 255: clear the frame
    print('EPD size:', epd.width,":",epd.height)
    draw = ImageDraw.Draw(Himage)


    # logging.info("read bmp file")
    # Himage = Image.open(os.path.join(picdir, '7in5_V2.bmp'))
    # epd.display(epd.getbuffer(Himage))
    # time.sleep(2)

    # ####################################
    # # drawing all boarders for refernce 
    # ####################################
    resolution = (epd.width, epd.height) #resolution of display
    buffer = 10  # buffer of 10 pixels.....

    # Clock widget
    # coord_box_prev = (0 + buffer ,0 + buffer)
    # size_box = (380,130)
    # draw_box(size = (size_box), position = (coord_box_prev[0], coord_box_prev[1]))
    

    # #internal clock system
    # time_hm = time.strftime("%H:%M", time.localtime())
    # time_pm = time.strftime("%p", time.localtime())
    # draw.text(xy = coord_box_prev, text = f"{time_hm}", font=set_of_fonts[120], fill=0)
    # draw.text(xy = (310,80), text = f"{time_pm}", font=set_of_fonts[40], fill=0)

    # # Date widget
    # coord_box_prev = (coord_box_prev[0], coord_box_prev[1] + size_box[1] + buffer)
    # size_box = (380, 80) 
    # draw_box(size = (size_box), position = coord_box_prev)

    # # weather
    # coord_box_prev = (coord_box_prev[0], coord_box_prev[1] + size_box[1] + buffer)
    # size_box = (380, 130) 
    # time_hms = time.strftime("%H:%M:%S", time.localtime())
    # draw.text(xy = coord_box_prev, text = f"{time_hms}", font=set_of_fonts[40], fill=0)
    
    # draw_box(size = (size_box), position = coord_box_prev)

    # # News Headline 
    # coord_box_prev = (coord_box_prev[0], coord_box_prev[1] + size_box[1] + buffer)
    # size_box = (380, 90) 
    # draw_box(size = (size_box), position = coord_box_prev)

    # # to do list 
    # coord_box_prev = ( 380 + (buffer*2 + buffer) , 0 + buffer)
    # size_box = (380, 225) 
    # draw_box(size = (size_box), position = coord_box_prev)

    # # Music/News
    # coord_box_prev = (coord_box_prev[0], coord_box_prev[1] + size_box[1] + buffer)
    # size_box = (380, 225) 
    # draw_box(size = (size_box), position = coord_box_prev)

    # putting album art 

    # include an image below the title
    weather_image_path = os.path.join(picdir, 'test.bmp')  # Path to your weather icon
    if os.path.exists(weather_image_path):
        image_temp = Image.open(weather_image_path)
        #put him to the center, and make him 1/3

        resize_factor = (380/800) * 0.98
        new_size = (int(image_temp.width * resize_factor), int(image_temp.height * resize_factor))
        image_temp = image_temp.resize(new_size, Image.ANTIALIAS)  # Resize if necessary

        position_image = (((380 + 3*buffer + 190) - image_temp.width//2),
                          ((245 + 112) - image_temp.height//2))  # Center the image horizontally
        Himage.paste(image_temp, position_image)  # Paste the icon at position (10, 90)
        epd.display(epd.getbuffer(Himage))

    # save output 
    Himage.save("my_generated_image.png")
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






