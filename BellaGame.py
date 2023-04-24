#!/usr/bin/python3

# To make this work you will need
#1)
# sudo apt install -y python3-picamera2
# sudo raspi-config
# and disable legacy camera support
#2)
# meArm.py and kinematics.py and grip.py
# in the same folder as this program
#
# Urs Utzinger 4/14/2023
# Last edited by Bella Klein 4/24/2023

display_debug = True
text_debug = False
############
# Camera setup was removed
############


#############
# Buttons and Switch
#############

# Importing libraries

import time             # import timing
import RPi.GPIO as GPIO # import Raspberry Pi input out put
import cv2

# Global Variables
# Buttons
start_pin  = 21
# Switch
switch_pin = 20

# Initialize Button and Switch
GPIO.setmode(GPIO.BCM)
# Button is input
GPIO.setup(start_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(switch_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#############
# meArm
#############

from pynput.keyboard import Listener
import meArm
import time

arm = meArm.meArm() # takes inserted data from meArm.py aka calibration data
arm.begin(0,0x70) #

# Defense
#########
xl = -65  # x coordinate of left position
yl = 165  # y coordinate of left position
zl = -10  # z coordinate of left position

xr =  65  # x coordinate of right position
yr = 165  # y coordinate of right position
zr = -10  # z coordinate of right position

# Throwing
#########
ready_toThrow =  False

# Idle Position
xi =  10 # x coordinate
yi = 170 # y coordinate
zi = -25 # z coordinate
# Start Position
xs = 100 # x coordinate
ys =  80 # y coordinate
zs = 140 # z coordinate
# End Position
xe = -55 # x coordinate
ye = 170 # y coordinate
ze =  80 # z coordinate


# Main Loop
#########################################################
stop = False

while (not stop):
    
    # Read Switch
    start_state  = GPIO.input(start_pin)
    switch_state = GPIO.input(switch_pin)
    str_start    = "pushed" if start_state else "not pushed"
    str_switch   = "Defense" if switch_state else "Attack"
    if text_debug: print("Start is {} and Switch is {}".format(str_start, str_switch))

    if switch_state:
        ####################################################
        # Defense
        ####################################################
        # arm moves side to side at the bottom of the goal to stop  
        # opponent's ball from hitting the field
        while (switch_state):
            ready_toThrow = False
            arm.gotoPoint(0, 165, -10)
            arm.gotoPoint( xr, yr, zr)
            arm.gotoPoint( xl, yl, zl)
            switch_state = GPIO.input(switch_pin)
        
        
        
    else:
        ####################################################
        # Attack
        ####################################################
        # moves arm to starting position if not already there
        if ready_toThrow == False: 
            arm.goDirectlyTo(arm.x,arm.y-25,arm.z)
            time.sleep(0.5)
            arm.goDirectlyTo(xi,yi,zi)
            ready_toThrow = True
        # once button is pushed, runs the throw sequence
        if start_state and ready_toThrow:
            # Ready 
            # Set ...
            arm.gotoPoint(xs,ys,zs)
            time.sleep(0.5)
            # Go!!
            arm.goDirectlyTo(xe,ye,ze)
            time.sleep(0.2)
            # Relax
            arm.gotoPoint(xi,yi,zi)

    # Check if user wantS to quit
    if display_debug:
        try:
            if (cv2.waitKey(1) & 0xFF == ord('q')) : stop = True
        except: stop = True 

# Clean up
cv2.destroyAllWindows()
GPIO.cleanup()
