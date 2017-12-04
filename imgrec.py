
# coding: utf-8

# In[ ]:


#!/usr/bin/python

#######################################
# Script for automatically recording  #
# slow framerate videos with the rpi  #
# Author: J. W. Jolles                #
# Last updated: 4 Dec 2017            #
#######################################

# import packages
import picamera
from time import sleep, strftime
import datetime
from socket import gethostname
import argparse
import os
import csv
from ast import literal_eval

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-w", "--imgwait", type=float, default=5.0,
        help="The delay between subsequent images in seconds")
ap.add_argument("-i", "--imgnr", type=int, default=10,
        help="The number of images that should be taken. ")
ap.add_argument("-t", "--imgtime", type=int, default=1,
        help="The duration in minutes during which images\
              should be taken.")
args = vars(ap.parse_args())
imgwait = args["imgwait"]
imgnr = args["imgnr"]
imgtime = args["imgtime"]


# define recording function
def record(location = "pi",
           imgwait = imgwait,
           imgnr = imgnr,
           imgtime = imgtime,
           resolution = (1000, 1000),
           compensation = 0,
           shutterspeed = 10000,
           iso = 200,
           brightness = 40,
           sharpness = 0,
           contrast = 20,
           saturation = -100,
           quality = 15,
           roifile = "/home/pi/roifile.txt"):
    
    """
        Run automated image recording with the rpi camera
                
        Parameters
        ----------
        location : str, default = pi
            The location where the images should be stored. By default
            (when location is "pi") the folder where the images are 
            stored is automatically set to the folder on the server 
            that reflects the rpi name, for example 
            /home/pi/SERVER/pi41. If different, a folder with 
            corresponding location name will be created in the home 
            directory.
        imgwait : float, default = 5.0
            The delay between subsequent images in seconds. When a 
            delay is provided that is less than shutterspeed + 
            processingtime "delay" will be automatically set at 0 
            and images thus taken one after the other.
        imgnr : integer, default = 100
            The number of images that should be taken. When this 
            number is reached the script will automatically terminate.
            The minimum of imgnr and nr of images based on imgwait and
            imgtime will be selected.
        imgtime : integer, default = 10
            The time in minutes during which images should be taken.
            The minimum of imgnr and nr of images based on imgwait and
            imgtime will be selected.
        resolution : tuple, default = (1000, 1000)
            The width and height of the images that will be recorded.
        compensation : int, default = 0
            Camera lighting compensation. Ranges between 0 and 20.
            Compensation artificially adds extra light to the image.
        shutterspeed : int, detault = 10000
            Shutter speed of the camera in microseconds, i.e. the
            default of 10000 is equivalent to 1/100th of a second. A
            longer shutterspeed will result in a brighter image but
            more likely motion blur.
        iso : int, default = 200
            The camera iso value. Higher values are more light
            sensitive but have higher gain. Valid values are
            between 200 and 1600.
        brightness : int, default = 55
            The brightness level of the camera. Valid values are
            between 0 and 100.
        sharpness : int, default = 50
            The sharpness of the image, an integer value between -100
            and 100.
        contrast : int, default = 20
            The image contrast, an integer value between 0 and 100.
        saturation : int, default -100
            The color saturation level of the image, an integer
            value between -100 and 100.
        quality : int, default = 20
            Defines the quality of the JPEG encoder as an integer
            ranging from 1 to 100. Defaults to 20.
        roifile : str, default = /home/pi/roifile.txt
            The filename for the txt file that contains the roi
            that should be used to crop the image. In that file
            the roi should be provided as (x, y, w, h) tuple of 
            floating point values ranging from 0.0 to 1.0, 
            The default value is (0.0, 0.0, 1.0, 1.0).
        
        Output
        -------
        A series of JPEG images, automatically named based on 
        the rpi number, date, and time, following a standard 
        naming convention, e.g. pi11_172511_im00010_153012.jpg
        
        """
    
    # acquire rpi name
    rpi = gethostname()
    
    print strftime("[%H:%M:%S][") + rpi + "] - imgrec started. The date is "+strftime("%y/%m/%d")           
    
    # convert to right type
    imgwait = float(imgwait)
    imgnr = int(imgnr)
    imgtime = int(imgtime)
    
    # when imgwait is close to zero, change to mininum
    # value that roughly equals time to take image
    imgwait = 0.3 if imgwait < 0.3 else imgwait

    # get number of images to record
    totimg = int(imgtime * (60 / imgwait))
    imgnr = min(imgnr, totimg)
    
    # set the directory
    if location == "pi":
        server = "/home/pi/SERVER/"
        location = server + rpi
    if os.path.exists(location):
        os.chdir(location)
    
    # set-up automatic filenaming
    daystamp = "_{timestamp:%Y%m%d}"
    counter = "_im{counter:05d}"
    timestamp = "_{timestamp:%H%M%S}"
    ftype = ".jpg"
    filename = rpi+daystamp+counter+timestamp+ftype
    
    # set the roi
    reader = csv.reader(open(roifile, "r"))
    zoom = next(reader)[0]
    zoom = literal_eval(zoom)        
    
    # set-up the camera with the right parameters
    camera = picamera.PiCamera()
    camera.resolution = resolution
    camera.zoom = zoom
    camera.exposure_compensation = compensation
    sleep(1)
    camera.exposure_mode = 'off'
    camera.awb_mode = 'off'
    camera.shutter_speed = shutterspeed
    camera.sharpness = sharpness
    camera.iso = iso
    camera.contrast = contrast
    camera.saturation = saturation
    camera.brightness = brightness
    
    # start taking images
    bef = datetime.datetime.now()
    for i, img in enumerate(camera.capture_continuous(filename, 
                            format="jpeg", quality=quality)):
        if i == (imgnr-1):
            print strftime("[%H:%M:%S][") + rpi + "] - captured " + img
            break
        delay = imgwait-(datetime.datetime.now()-bef).total_seconds()
        delay = 0 if delay < 0 else delay
        print strftime("[%H:%M:%S][") + rpi + "] - captured " + img +              ", sleeping " + str(round(delay,2)) + "s.."
        sleep(delay)
        bef = datetime.datetime.now()
    
    print "==================================================\n"

record()

