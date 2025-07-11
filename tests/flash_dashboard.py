#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
from PIL import Image # to change photos

picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'assets/pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'assets/lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd7in5_V2_old
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / 'src' / 'modules'))
import printing_image as pim


# ACTUAL SCRIPTS
logging.basicConfig(level=logging.DEBUG)

# Displaying a simple image
epd = epd7in5_V2_old.EPD()
screen_render = pim.ScreenRender(epd = epd, 
                                 picdir = picdir, 
                                 libdir=libdir)

screen_render.screen_clear()

#render image
filepath_image = Image.open(os.path.join(picdir, 'test.bmp'))
screen_render.screen_render_image(filepath_image=filepath_image)

print('end')


try:
    logging.info("epd7in5_V2 Demo")
    epd = epd7in5_V2_old.EPD()
    
    logging.info("init and Clear")
    epd.init()
    epd.Clear()

    font20 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 20)
    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
    font16 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 16)
    font14 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 14)
    font12 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 12)
    
    # Displaying a simple image
    # logging.info("read bmp file")
    # Himage = Image.open(os.path.join(picdir, 'test.bmp'))
    # epd.display(epd.getbuffer(Himage))
    # time.sleep(2)

    # Drawing on the Horizontal image
    # logging.info("1.Drawing on the Horizontal image...")
    # Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    # draw = ImageDraw.Draw(Himage)
    # draw.text((10, 0), 'WHAT THE FUCK DID YOU JUST SAY YOU STUPID', font = font24, fill = 0)
    # draw.text((10, 20), 'IMA FIGHT YOU FOR REAL FOR REAL', font = font24, fill = 0)
    
    # draw.line((20, 50, 70, 100), fill = 0)
    # draw.line((70, 50, 20, 100), fill = 0)
    # draw.rectangle((20, 50, 70, 100), outline = 0)
    # draw.line((165, 50, 165, 100), fill = 0)
    # draw.line((140, 75, 190, 75), fill = 0)
    # draw.arc((140, 50, 190, 100), 0, 360, fill = 0)
    # draw.rectangle((80, 50, 130, 100), fill = 0)
    # draw.chord((200, 50, 250, 100), 0, 360, fill = 0)
    # epd.display(epd.getbuffer(Himage))
    # time.sleep(2)


    logging.info("Drawing Weather Dashboard...")

    # Create new image (assuming similar dimensions to your setup)
    Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(Himage)

    # Weather Dashboard Title
    draw.text((10, 5), 'WEATHER DASHBOARD', font=font24, fill=0)
    draw.line((10, 30, 250, 30), fill=0)  # Underline

    # Current Weather Section
    draw.text((10, 40), 'Current: Sunny', font=font20, fill=0)
    draw.text((10, 60), 'Temperature: 72°F', font=font16, fill=0)
    draw.text((10, 75), 'Humidity: 45%', font=font16, fill=0)
    draw.text((10, 90), 'Wind: 8 mph NW', font=font16, fill=0)

    # Sun icon (circle with rays)
    sun_center_x, sun_center_y = 200, 70
    sun_radius = 15
    # Sun circle
    draw.ellipse((sun_center_x - sun_radius, sun_center_y - sun_radius, 
                sun_center_x + sun_radius, sun_center_y + sun_radius), outline=0)
    # Sun rays
    for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
        import math
        ray_length = 8
        start_x = sun_center_x + (sun_radius + 2) * math.cos(math.radians(angle))
        start_y = sun_center_y + (sun_radius + 2) * math.sin(math.radians(angle))
        end_x = sun_center_x + (sun_radius + ray_length + 2) * math.cos(math.radians(angle))
        end_y = sun_center_y + (sun_radius + ray_length + 2) * math.sin(math.radians(angle))
        draw.line((start_x, start_y, end_x, end_y), fill=0)

    # Divider line
    draw.line((10, 110, 250, 110), fill=0)

    # 3-Day Forecast
    draw.text((10, 120), '3-DAY FORECAST', font=font18, fill=0)

    # Day 1
    draw.text((10, 145), 'MON', font=font16, fill=0)
    draw.text((10, 160), '75°/58°', font=font14, fill=0)
    # Partly cloudy icon (circle with cloud)
    draw.ellipse((50, 145, 70, 165), outline=0)
    draw.ellipse((60, 140, 85, 160), outline=0)

    # Day 2  
    draw.text((100, 145), 'TUE', font=font16, fill=0)
    draw.text((100, 160), '68°/52°', font=font14, fill=0)
    # Rain cloud icon
    draw.ellipse((140, 145, 165, 165), outline=0)
    draw.line((145, 170, 145, 175), fill=0)  # Rain drops
    draw.line((150, 168, 150, 173), fill=0)
    draw.line((155, 170, 155, 175), fill=0)

    # Day 3
    draw.text((180, 145), 'WED', font=font16, fill=0)
    draw.text((180, 160), '71°/55°', font=font14, fill=0)
    # Sunny icon (smaller sun)
    draw.ellipse((220, 150, 235, 165), outline=0)

    # Bottom section with additional info
    draw.line((10, 185, 250, 185), fill=0)
    draw.text((10, 195), 'UV Index: 6 (High)', font=font14, fill=0)
    draw.text((10, 210), 'Sunrise: 6:24 AM', font=font14, fill=0)
    draw.text((130, 210), 'Sunset: 8:17 PM', font=font14, fill=0)

    # Air quality indicator
    draw.text((10, 225), 'Air Quality: Good', font=font14, fill=0)
    draw.rectangle((120, 225, 140, 235), outline=0)  # Good indicator box
    draw.rectangle((121, 226, 139, 234), fill=0)     # Filled indicator

    # Pressure and visibility
    draw.text((10, 245), 'Pressure: 30.15 in', font=font12, fill=0)
    draw.text((130, 245), 'Visibility: 10 mi', font=font12, fill=0)

    # Last updated timestamp
    draw.text((10, 265), 'Updated: 2:30 PM', font=font12, fill=0)

    # Weather alert box (if needed)
    draw.rectangle((10, 280, 250, 300), outline=0)
    draw.text((15, 285), 'No weather alerts', font=font12, fill=0)

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

print('done')
