#!/usr/bin/env python3

from omxplayer.player import OMXPlayer
from pathlib import Path
from gpiozero import Button
from time import sleep, time
import os
#import logging
#logging.basicConfig(level=logging.INFO)

PAUSE_TIMEOUT = 3
PAUSE_TIME = int(time())
print("start pause time %s " % PAUSE_TIME)

VIDEO_DIR = "/home/pi/"
VIDEO_FILE = "qq1.mp4"
VIDEO_PATH = VIDEO_DIR + VIDEO_FILE

button = Button(26)

while True:
            print(VIDEO_PATH)
            player = OMXPlayer(VIDEO_PATH,dbus_name='org.mpris.MediaPlayer2.omxplayer1',args='-b --loop')
            PLAYER_STATUS = player.playback_status()
            print("nastaven player")

            while not player.can_control():
                print("Can control %s " % player.can_control())
                sleep(0.1)

            print("Start player status %s" % player.playback_status())

            try:
                while player.can_control():
                    if button.is_pressed:
                        print("button pressed")
                        player.play_pause()
                        print("duration %s" % player.position())
                        if not player.is_playing():
                            PAUSE_TIME = int(time())
                    if PLAYER_STATUS != player.playback_status():
                        print("player status %s" % player.playback_status())
                        PLAYER_STATUS = player.playback_status()
                    if not player.is_playing():
                        if int(time()) - PAUSE_TIME > PAUSE_TIMEOUT:
                            player.play()
                    sleep(0.2)
            
            except:
                print("Exception")

#player.quit()

print("End")
