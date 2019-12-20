#!/usr/bin/env python3

# v0.1.0, 15.11.2018, Martin Mikala, initial version
# v0.1.1, 25.11.2018, Martin Mikala, set path to video as path type 
# v0.2.0,  9.12.2018, Martin Mikala, change to three buttons version

#from omxplayer.player import OMXPlayer
import omxplayer.player
import omxplayer.keys
from pathlib import Path
from gpiozero import Button
#from time import sleep, time
import time
from os import system
#import logging
#logging.basicConfig(level=logging.INFO)

time_jump = 0.5
time_current = time.clock_gettime(0) 
time_last = time_current
#print("start pause time %s " % PAUSE_TIME)

VIDEO_DIR = "/home/pi/"
VIDEO_FILE = "qq1.mp4"
VIDEO_PATH = Path(VIDEO_DIR + VIDEO_FILE)
#VIDEO_ACTION = [8,21,40,52,72,87]
#ACTION_TOLERANCE = 0.5

buttonP = Button(26)    # button for pause/start
buttonF = Button(13)    # button forward
buttonR = Button(19)    # button rewind back

#while True:
player = omxplayer.player.OMXPlayer(VIDEO_PATH,dbus_name='org.mpris.MediaPlayer2.omxplayer1',args='--loop')

while not player.can_control():
    print("Can control %s " % player.can_control())
    sleep(0.1)

print("Start player status %s" % player.playback_status())

pushP = False
lastP = pushP
pushR = False
lastR = pushR
pushF = False
lastF = pushF

move_mode = False
ff_mode = False
play_mode = False

player.action(omxplayer.keys.SHOW_INFO)

#try:
while player.can_control():
	time_current = time.clock_gettime(0)
	if time_current - time_last > time_jump:
		#print("last %f curr %f jump %f minus %f" % (time_last,time_current,time_jump,(time_current - time_last)))
		time_last = time_current
		pushP = buttonP.is_pressed
		pushR = buttonR.is_pressed
		pushF = buttonF.is_pressed
	
		if pushP != lastP:             #chanche Play/Pause button
			print("buttonP")
			print("player status 1 %s" % player.playback_status())
			if pushP:					# button pushed
				player.pause()		# change mode to pause
			else:						# button released
				player.play()		# change mode to play
			print("player status 2 %s" % player.playback_status())
			lastP = pushP				# note button state
			#sleep(0.2)
	
		if pushF != lastF:				#change FF button
			print("buttonF")
			print("player status 1 %s" % player.position())
			if pushF:					# button pushed
				#player.action(omxplayer.keys.FAST_FORWARD)
				#player.action(omxplayer.keys.FAST_FORWARD)
				player.set_rate(4)
				#player.pause()
				#position = player.position()
				#player.set_position(position+0.1)
				#player.seek(1)
				#player.play()
			else:
				#player.action(omxplayer.keys.REWIND)
				player.set_rate(1)
				pass
			#player.seek(0.01)
			print("player status 2 %s" % player.position())
			lastF = pushF			#note button state
			#sleep(0.1)
	
		if pushR != lastR:              #change FF button
			print("buttonR")
			print("player status 1 %s" % player.position())
			if pushR:                   # button pushed
				#player.action(omxplayer.keys.REWIND)
				player.seek(-1)
			else:
				#player.play()
				#player.action(omxplayer.keys.FAST_FORWARD)
				#player.seek(0.01)
				pass
			print("player status 2 %s" % player.position())
			lastR = pushR           #note button state
		print("player position %s , rate %d " % (player.position(), player.rate()))
		#print("rate %d" % player.rate())
		#print(player.is_playing())
		#print(player.maximum_rate())
		#sleep(0.1)
	
player.quit()
print("End")

