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
# Template: Urs Utzinger 4/14/2023
# Edited by Bella Klein 4/26/2023

display_debug = True
text_debug = False
############
# Camera setup was removed
############
import cv2

#############
# Buttons and Switch
#############
# Importing libraries

import time             # import timing
import RPi.GPIO as GPIO # import Raspberry Pi input out put

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
#x,y,z coordinates of left defence position
xl = -65
yl = 160
zl = 10
#x,y,z coordinates of right defence position
xr = 65
yr = 160
zr = 10
 
# Throwing
##############
ready_toThrow =  False

# Idle Position
xi =  10 # x coordinate
yi = 170 # y coordinate
zi = -25 # z coordinate
# Start Position
xs = 100 # x coordinate
ys =  70 # y coordinate
zs = 140 # z coordinate
# End Position
xe = -60 # x coordinate
ye = 145 # y coordinate
ze = 100 # z coordinate

############
# Position Filtering, remove outlayers
############
# import collections
# import statistics
# this will slow response down, perhaps better to not filter
# pos_x = collections.deque(maxlen=3) # if you want to take median of 3 locations. 
# pos_y = collections.deque(maxlen=3)
# pos_x.append(x_offset) # initialize
# pos_y.append(z_offset)
#pos_x = x_offset # No position filtering
#pos_y = z_offset

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
        while (switch_state):
            ready_toThrow = False
            arm.gotoPoint(0, 160, 10)
            arm.gotoPoint(xr, yr, zr)
            arm.gotoPoint(xl, yl, zl)
            switch_state = GPIO.input(switch_pin)
        
    else:
        ####################################################
        # Attack
        ####################################################
        if ready_toThrow == False:
            #moves to start position, making sure not to hit the goal
            arm.goDirectlyTo(arm.x,arm.y-25,arm.z)
            time.sleep(0.9) 
            arm.goDirectlyTo(xi,yi,zi) 
            ready_toThrow = True
        if start_state and ready_toThrow:
            # Ready 
            # Set ...
            arm.gotoPoint(xs,ys,zs)
            time.sleep(0.5) # makes sure ball is settled on the holder before throwing
            # Go!!
            arm.goDirectlyTo(xe,ye,ze) #moves rapidly to end position
            time.sleep(0.2)
            # Relax
            arm.gotoPoint(xi,yi,zi) #back to starting position

    # Check if user wants to quit
    if display_debug:
        try:
            if (cv2.waitKey(1) & 0xFF == ord('q')) : stop = True
        except: stop = True 

# Clean up
cv2.destroyAllWindows()
GPIO.cleanup()

