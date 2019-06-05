#!/usr/bin/env python
import pygame
import time
import os
import shutil
import PIL.Image
import RPi.GPIO as GPIO
import subprocess
import sys

from threading import Thread
from pygame.locals import *
from time import sleep
from PIL import Image, ImageDraw


# initialise global variables
Numeral = ""  # Numeral is the number display
Message = ""  # Message is a fullscreen message
BackgroundColor = ""
CountDownPhoto = ""
CountPhotoOnCart = ""
SmallMessage = ""  # SmallMessage is a lower banner message
Filename = ""
TmpFilename = "/home/pi/git-repos/photoboothdiy/tmp/pic.jpg"
imagefolder = "/media/usb32/photobooth/"
TotalImageCount = 0  # Counter for Display 
imagecounter = 0
ImageShowed = False
Printing = False
BUTTON_PIN = 16
#IMAGE_WIDTH = 558
#IMAGE_HEIGHT = 374
IMAGE_WIDTH = 550
IMAGE_HEIGHT = 360

pygame.init()  # Initialise pygame
pygame.font.init()
pygame.mouse.set_visible(False) #hide the mouse cursor
infoObject = pygame.display.Info()
screen = pygame.display.set_mode((infoObject.current_w,infoObject.current_h), pygame.FULLSCREEN)  # Full screen 
background = pygame.Surface(screen.get_size())  # Create the background object
background = background.convert()  # Convert it to a background

screenPicture = pygame.display.set_mode((infoObject.current_w,infoObject.current_h), pygame.FULLSCREEN)  # Full screen
backgroundPicture = pygame.Surface(screenPicture.get_size())  # Create the background object
backgroundPicture = background.convert()  # Convert it to a background

transform_x = infoObject.current_w # how wide to scale the jpg when replaying
transfrom_y = infoObject.current_h # how high to scale the jpg when replaying


    
# A function to handle keyboard/mouse/device input events
def input(events):
    for event in events:  # Hit the ESC key to quit the slideshow.
        if (event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE)):
            pygame.quit()

			
# set variables to properly display the image on screen at right ratio
def setDimensions(img_w, img_h):
    # Note this only works when in booting in desktop mode. 
    # When running in terminal, the size is not correct (it displays small). Why?

    # connect to global vars
    global transform_y, transform_x, offset_y, offset_x

    # based on output screen resolution, calculate how to display
    ratio_h = (infoObject.current_w * img_h) / img_w 

    if (ratio_h < infoObject.current_h):
        #Use horizontal black bars
        #print "horizontal black bars"
        transform_y = ratio_h
        transform_x = infoObject.current_w
        offset_y = (infoObject.current_h - ratio_h) / 2
        offset_x = 0
    elif (ratio_h > infoObject.current_h):
        #Use vertical black bars
        #print "vertical black bars"
        transform_x = (infoObject.current_h * img_w) / img_h
        transform_y = infoObject.current_h
        offset_x = (infoObject.current_w - transform_x) / 2
        offset_y = 0
    else:
        #No need for black bars as photo ratio equals screen ratio
        #print "no black bars"
        transform_x = infoObject.current_w
        transform_y = infoObject.current_h
        offset_y = offset_x = 0

def InitFolder():
    global imagefolder
    global Message
 
    Message = 'Folder Check...'
    UpdateDisplay()
    Message = ''

    #check image folder existing, create if not exists
    if not os.path.isdir(imagefolder):	
        os.makedirs(imagefolder)	
            
#     imagefolder2 = os.path.join(imagefolder, 'images')
#     if not os.path.isdir(imagefolder2):
#         os.makedirs(imagefolder2)
		
def DisplayText(fontSize, textToDisplay):
    global Numeral
    global Message
    global screen
    global background
    global pygame
    global ImageShowed
    global screenPicture
    global backgroundPicture
    global CountDownPhoto

    if (BackgroundColor != ""):
        #print(BackgroundColor)
        background.fill(pygame.Color("black"))
    if (textToDisplay != ""):
        #print(displaytext)
        font = pygame.font.Font(None, fontSize)
        text = font.render(textToDisplay, 1, (227, 157, 200))
        textpos = text.get_rect()
        textpos.centerx = background.get_rect().centerx
        textpos.centery = background.get_rect().centery
        if(ImageShowed):
                backgroundPicture.blit(text, textpos)
        else:
                background.blit(text, textpos)
				
def UpdateDisplay():
    # init global variables from main thread
    global Numeral
    global Message
    global screen
    global background
    global pygame
    global ImageShowed
    global screenPicture
    global backgroundPicture
    global CountDownPhoto
   
    background.fill(pygame.Color("white"))  # White background
    #DisplayText(100, Message)
    #DisplayText(800, Numeral)
    #DisplayText(500, CountDownPhoto)

    if (BackgroundColor != ""):
        #print(BackgroundColor)
        background.fill(pygame.Color("black"))
    if (Message != ""):
        #print(displaytext)
        font = pygame.font.Font(None, 100)
        text = font.render(Message, 1, (227, 157, 200))
        textpos = text.get_rect()
        textpos.centerx = background.get_rect().centerx
        textpos.centery = background.get_rect().centery
        if(ImageShowed):
            backgroundPicture.blit(text, textpos)
        else:
            background.blit(text, textpos)

    if (Numeral != ""):
        #print(displaytext)
        font = pygame.font.Font(None, 800)
        text = font.render(Numeral, 1, (227, 157, 200))
        textpos = text.get_rect()
        textpos.centerx = background.get_rect().centerx
        textpos.centery = background.get_rect().centery
        if(ImageShowed):
            backgroundPicture.blit(text, textpos)
        else:
            background.blit(text, textpos)

    if (CountDownPhoto != ""):
        #print(displaytext)
        font = pygame.font.Font(None, 500)
        text = font.render(CountDownPhoto, 1, (227, 157, 200))
        textpos = text.get_rect()
        textpos.centerx = background.get_rect().centerx
        textpos.centery = background.get_rect().centery
        if(ImageShowed):
            backgroundPicture.blit(text, textpos)
        else:
            background.blit(text, textpos)
    
    if(ImageShowed == True):
    	screenPicture.blit(backgroundPicture, (0, 0))   	
    else:
    	screen.blit(background, (0, 0))
   
    pygame.display.flip()
    return


def ShowPicture(file, delay):
    global pygame
    global screenPicture
    global backgroundPicture
    global ImageShowed
    backgroundPicture.fill((0, 0, 0))
    img = pygame.image.load(file)
    img = pygame.transform.scale(img, screenPicture.get_size())  # Make the image full screen
    backgroundPicture.blit(img, (0,0))
    screen.blit(backgroundPicture, (0, 0))
    pygame.display.flip()  # update the display
    ImageShowed = True
    time.sleep(delay)
	
# display one image on screen
def show_image(image_path):	
	screen.fill(pygame.Color("white")) # clear the screen	
	img = pygame.image.load(image_path) # load the image
	img = img.convert()	
	setDimensions(img.get_width(), img.get_height()) # set pixel dimensions based on image	
	x = (infoObject.current_w / 2) - (img.get_width() / 2)
	y = (infoObject.current_h / 2) - (img.get_height() / 2)
	screen.blit(img,(x,y))
	pygame.display.flip()

def CapturePicture():
    global imagecounter
    global imagefolder
    global Numeral
    global Message
    global screen
    global background
    global screenPicture
    global backgroundPicture
    global pygame
    global ImageShowed
    global CountDownPhoto
    global BackgroundColor	
    global Filename
    global TmpFilename
    
    BackgroundColor = ""
    Numeral = ""
    Message = ""
    UpdateDisplay()
    time.sleep(1)
    CountDownPhoto = ""
    UpdateDisplay()
    background.fill(pygame.Color("black"))
    screen.blit(background, (0, 0))
    pygame.display.flip()        
    BackgroundColor = "black"

    for x in range(3, 0, -1):
        # if x == 0:                        
        #         Numeral = ""
        #         Message = "PRENEZ LA POSE"
        # else:                        
        Numeral = str(x)
        Message = ""                
        UpdateDisplay()
        time.sleep(1)

    BackgroundColor = ""
    Numeral = ""
    Message = ""
    UpdateDisplay()
    imagecounter = imagecounter + 1
    
    if os.path.isfile(TmpFilename):
        os.remove(TmpFilename)

    subprocess.call("/home/pi/git-repos/photoboothdiy/gphoto2.sh", shell=True)
    
    if not os.path.isfile(TmpFilename):
        Filename = "ERROR"
    else:
        #Generate final image name        
        Filename = os.path.join(imagefolder, time.strftime("Photobooth_%Y%m%d_%H%M%S.jpg"))
        print("Filename = " + Filename)

        #Tweak to avoid errors when writing on 
        osChmodBackup = os.chmod
        del os.chmod

        #Move file
        shutil.move(TmpFilename, Filename)       

        # Set things back to normal
        setattr(os, 'chmod', osChmodBackup)

    return Filename 
    
        
def TakePictures():
    global imagecounter
    global imagefolder
    global Numeral
    global Message
    global screen
    global background
    global pygame
    global ImageShowed
    global CountDownPhoto
    global BackgroundColor
    global Printing
    global TotalImageCount

    input(pygame.event.get())
    # print("TakePictures pygame.event.get() => " + pygame.event.get())

    CountDownPhoto = "1/3"        
    filename1 = CapturePicture()        

    CountDownPhoto = "2/3"
    filename2 = CapturePicture()

    CountDownPhoto = "3/3"
    filename3 = CapturePicture()

    CountDownPhoto = ""
    UpdateDisplay()

    TotalImageCount = TotalImageCount + 1        

    if filename1 != "ERROR":
        ShowPicture(filename1 , 2)
    if filename2 != "ERROR":
        ShowPicture(filename2 , 2)
    if filename3 != "ERROR":
        ShowPicture(filename3 , 2)
    ImageShowed = False

    # Create the final filename
    ts = time.time()

    # Final_Image_Name = os.path.join(imagefolder, time.strftime("Photobooth", ts))
    # Final_Image_Name = os.path.join(imagefolder, str(TotalImageCount)+"_"+str(ts) + ".png")
    # # Save it to the usb drive
    # bgimage.save(Final_Image_Name)

    ImageShowed = False
    
    UpdateDisplay()
    time.sleep(1)
    Message = "Merci !!"
    UpdateDisplay()
    Numeral = ""
    time.sleep(2)

    Message = "Nous vous enverrons vos photos ;)"
    Numeral = ""
    UpdateDisplay()
    time.sleep(2)
            
    Message = ""
    Numeral = ""
    ImageShowed = False
    UpdateDisplay()
    time.sleep(1)

# def MyCallback(channel):
#     global Printing
#     GPIO.remove_event_detect(BUTTON_PIN)
#     Printing=True
        
def WaitForEvent():
    global pygame

    #Setup GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    NotEvent = True
    while NotEvent:
        input_state = GPIO.input(BUTTON_PIN)
        print("input_state = " + str(input_state))
        if input_state:
            NotEvent = False	
            print("Not event = False => return")		
            return  
        for event in pygame.event.get():
            print("Loop through pygame.event.get")
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                if event.key == pygame.K_DOWN:
                        NotEvent = False
                        return
        
        time.sleep(0.2)

def main(threadName, *args):
    InitFolder()
    while True:
        show_image('images/start_camera.jpg')        
        WaitForEvent()
        time.sleep(0.2)
        print("PHOTO !")
        # TakePictures()
        pygame.quit()        
        
    GPIO.cleanup()


# launch the main thread
Thread(target=main, args=('Main', 1)).start()