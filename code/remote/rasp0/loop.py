# standart library imports
import os
import sys
import time

# third-party imports
from PIL import Image
import RPi.GPIO as GPIO
import numpy as np
import smbus  # I2C

# local imports
from UV_projector.controller import DLPC1438, Mode

GPIO.setmode(GPIO.BCM)

HOST_IRQ = 6  # GPIO pin for HOST_IRQ
PROJ_ON = 5  # GPIO pin for PROJ_ON

i2c = smbus.SMBus(8)  # we configured our software i2c to be on bus 8

### Controlling DMD ################################################################################

# Initialise the DLPC1438
DMD = DLPC1438(i2c, PROJ_ON, HOST_IRQ)
# Configure it (NOTE: Mode.STANDBY can clear these settings, so call it again after standby)
DMD.configure_external_print(LED_PWM=1023) #1023

# switch to right mode
DMD.switch_mode(Mode.EXTERNALPRINT)
DMD.expose_pattern(-1)  # expose for infinite duration (until we stop it)

### Writing data to framebuffer ####################################################################

# Map the screen as Numpy array
# the framebuffer is XR24 (BGRX) - https://www.linuxtv.org/downloads/v4l-dvb-apis-new/userspace-api/v4l/pixfmt-rgb.html
# (you can check this with `kmsprint`)

# in XR24, byte3 corresponds to the RED channel and since we have our raspberry pi DPI
# pins wired to the red channel, we need to write to those bytes with our code.

h, w, c = 720, 1280, 4
fb = np.memmap('/dev/fb0', dtype='uint8',mode='w+', shape=(h, w, c)) 

# we first zero the framebuffer (otherwise you can get an image of the terminal :P)
fb[:,:, 0] = 0 
fb[:,:, 1] = 0 
fb[:,:, 2] = 0 

# # blue  # should be dark
# fb[:,:, 0] = 255 
# fb[:,:, 1] = 0 
# fb[:,:, 2] = 0 

while True:

	recv = input()
	if recv == "q":
		break

	x1, y1, x2, y2, i = (int(num) for num in recv.split("_"))
	fb[x1:x2, y1:y2, 0] = i

	# filename, t_delay = sys.argv[1:]
	    
	# im_frame = Image.open(os.path.join("/media", "pics", filename))
	# pixeldata = np.array(im_frame.convert('L'))

# fb[:,:,2] = pixeldata
# time.sleep(int(t_delay)/1000)

fb[:,:,2] = 0

# turn light off
DMD.stop_exposure()  

time.sleep(0.3)
DMD.switch_mode(Mode.STANDBY)  # leave system in standby
