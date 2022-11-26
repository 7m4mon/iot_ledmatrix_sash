#!/usr/bin/env python3
# -*- encoding:utf8 -*-

# IoT ledmatrix sash [tasuki]
# Author : 7M4MON (2018-2022)

# This program shows a bitmap file or any strings on WS2812 LED MATRIX (8x32)
# Execute with add '-s' opthon, enables HTTP Server.
# When execute without option, shows rainbow and image file and string. (see main function)

# useage:
# sudo python iot_ledmatrix_sash.py -s

# Using Lbrary : Neopixel (https://github.com/jgarff/rpi_ws281x)
# PIL, numpy, cgi, cgitb, HTTPServer
# Using Fonts: Minecraftia-Regular.ttf; by Andrew Tyler (http://www.dafont.com/bitmap.php)

# Tested with Raspberry Pi Type B and Raspberry Pi Zero W 

import time
from neopixel import *
import argparse

from PIL import Image, ImageOps
from PIL import ImageDraw
from PIL import ImageFont
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

from numpy import *
import numpy as np
import numpy

import cgi
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler

import cgitb; cgitb.enable()

import os

# LED strip configuration:
LED_X          = 32
LED_Y          = 8
LED_COUNT      = LED_X * LED_Y      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 7     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = True   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

UPLOAD_DIR = "./image"

import RPi.GPIO as GPIO
PIN_POWER_SW = 3        # for wake up pin (I2C_SCL1)

exe = 1                 # execute flag

def shutdown_by_sw(det):
    ''' Shutdown call by switch intterupt '''
    if(GPIO.input(PIN_POWER_SW) == 0):
        shutdown_counter = 0
        drawText('SHUTDOWN', Color(0,0,255), Color(0,255,0))
        print('Hold 5 sec to shutdown')
        while GPIO.input(PIN_POWER_SW) == 0:
            shutdown_counter +=1
            time.sleep(100/1000.0)
            if shutdown_counter > 50:
                colorWipe(Color(0,0,0), 10)
                time.sleep(3000/1000.0)
                os.system("sudo shutdown now -h")

def check_power_sw():
    return 0 if GPIO.input(PIN_POWER_SW) else 1

''' define the pins for shutdown switch'''
GPIO.setmode(GPIO.BCM)
#GPIO23pinを入力モードとします。外部プルアップがあるので内蔵プルアップは無効です。
GPIO.setup(PIN_POWER_SW,GPIO.IN)
GPIO.add_event_detect(PIN_POWER_SW, GPIO.FALLING, callback=shutdown_by_sw, bouncetime=300) 


# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)

class MyHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/serial':
            # 飛ばされてきたリクエストを受け取る
            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers,
                                    environ={'REQUEST_METHOD':'POST'})
                                    
            if form.has_key('code'):
                code = form['code'].value
                print ('code: ' + str(code))
                
                # 受け取ったクエリに応じて点灯させるLEDを設定する
                if code == "led1":
                    filename = './image/H08x64_01_spectrum_chart-1.bmp'
                    showImageFile(filename)
                elif code == "led2":
                    filename = './image/H08x64_04_keep_right.bmp'
                    showImageFile(filename,500,100)
                elif code == "led3":
                    filename = './image/H08x64_05_keep_price.bmp'
                    showImageFile(filename, 500,200)
                elif code == "rainbow":
                    rainbow(10)
                elif code == "exit":
                    exe = 0
                    colorWipe(Color(0,0,0), 10)
                
            elif form.has_key('text'):
                 text_string  = form['text'].value
                 print ('text: ' + text_string)
                 drawText(text_string)
            
            self.send_response(100)
            self.send_header('Content-type', 'text/html')
            return
        return self.do_GET()


def colorWipe(color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)


def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def rainbow(wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i+j) & 255))
        if check_power_sw() :
            exe = 0
            return
        else:
            strip.show()
        time.sleep(wait_ms/1000.0)


def drawText(text, fore_color = (255,255,255), back_color = 0):
    # Create blank image for drawing.
    fontwidth = 10
    width = (len(text)+1) * fontwidth + LED_X
    height = LED_Y
    image = Image.new('RGB', (width, height), back_color)
    
    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    # Make sure the .ttf font file is in the same directory as the python script!
    # Some other nice fonts to try: http://www.dafont.com/bitmap.php
    draw.font = PIL.ImageFont.truetype('Minecraftia-Regular.ttf', 8, encoding='unic')
    text_img_size = draw.font.getsize(text)
    print('drawText: '+ text + '\r\n text_img_size: ' + str(text_img_size))
    
    draw.text((0, -2), text,  fill=fore_color)
    image = image.crop((0,0, text_img_size[0] + LED_X, height))
    #image.save('moji1.png')
    
    showImage(image)

img = PIL.Image.new("RGBA", (100, 8))
def draw_text_at_center(text):
    draw = PIL.ImageDraw.Draw(img)
    draw.font = PIL.ImageFont.truetype(
                'Minecraftia-Regular.ttf', 8, encoding='unic')
    
    img_size = numpy.array(img.size)
    txt_size = numpy.array(draw.font.getsize(text))
    pos = (img_size - txt_size) / 2
    
    draw.text(pos, text, (255, 255, 255))
    
    img.save('string_image.png')
    showImage(img)

def showImageFile(filename, wait_ms = 500, scroll_wait = 20, scroll_step = 1):
    """show image by filename (ex: './test.png' )"""
    img = Image.open(filename)
    #img = ImageOps.mirror(img)
    print('showImageFile :' + filename)
    showImage(img, wait_ms, scroll_wait, scroll_step)

def showImage(img, first_wait=500 , scroll_wait=20, scroll_step = 1):
    """show image by image object """
    img_array = np.asarray(img , dtype = 'uint32')
    print('showImage width :' + str(img_array.shape[1]))
    k = 0
    while k <= img_array.shape[1] - LED_X:
        for i in range(LED_X):
            for j in range(LED_Y):
                if i & 1 :              # Arrangement by zigzag
                    y = LED_Y - j -1
                else:
                    y = j
                    
                """check range x,y of image"""
                """
                if i >  img_array.shape[1] or y  > img_array.shape[0] :
                    col = Color(0,0,0)
                else:
                """
                col = Color(int(img_array[y,i+k,1]), int(img_array[y,i+k,0]), int(img_array[y,i+k,2]))    # [h,w,[r,g,b])
                
                
                strip.setPixelColor(i*LED_Y + j, col)
                
        if check_power_sw() :
            exe = 0
            return
        else:
            strip.show()
            
        if k == 0 :
            time.sleep(first_wait/1000.0)
        else:
            time.sleep(scroll_wait/1000.0)
            
        k += scroll_step


# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    parser.add_argument('-s', '--server', action='store_true', help='HTTP Web Server')
    args = parser.parse_args()

    # Intialize the library (must be called once before other functions).
    strip.begin()
    
    print ('Press Ctrl-C to quit.')
    
    
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')
    try:
        if args.server:
            print('Start HTTP Web Server:80')
            # HTTP サーバーの起動
            server = HTTPServer(('', 80), MyHandler).serve_forever()
        while exe:

            rainbow()

            filename = './image/H08x64_04_keep_right.bmp'
            showImageFile(filename,200,200)
            
            filename = './image/H08x64_05_keep_price.bmp'
            showImageFile(filename,200,200)
            
            drawText(u'ABCDEFG01234567890abcd', Color(0,255,0))

            if(GPIO.input(PIN_POWER_SW) == 0):
                exe = 0
                colorWipe(Color(0,0,0), 10)

    except KeyboardInterrupt:
        if args.clear:
            colorWipe(Color(0,0,0), 10)
            
            
