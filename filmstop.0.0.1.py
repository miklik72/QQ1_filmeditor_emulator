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

VIDEOS_DIR = "/home/pi/videos"
VIDEOS_LIST = os.listdir(VIDEOS_DIR)

for VIDEO_FILE in VIDEOS_LIST:
    print(VIDEO_FILE)
    VIDEO_PATH = VIDEOS_DIR + "/" + VIDEO_FILE
    print(VIDEO_PATH)
    #player_log = logging.getLogger("Player 1")
    button = Button(26)
    player = OMXPlayer(VIDEO_PATH,dbus_name='org.mpris.MediaPlayer2.omxplayer1')
    player.action(5)
    PLAYER_STATUS = player.playback_status()
    print("nastaven player")

    while not player.can_control():
        print("Can control %s " % player.can_control())
        sleep(0.1)

    # it takes about this long for omxplayer to warm up and start displaying a picture on a rpi3
    #sleep(2.5)
    print("Start player status %s" % player.playback_status())

    #print("Playing")
    #sleep(10)

    #button.when_pressed = player.play_pause()

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
    
    #except dbus.exceptions.DBusException:
    except:
        print("Exception")

    #player.quit()

print("End")
