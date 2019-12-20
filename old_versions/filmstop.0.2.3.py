#!/usr/bin/env python3

# v0.1.0, 15.11.2018, Martin Mikala, initial version
# v0.1.1, 25.11.2018, Martin Mikala, set path to video as path type 
# v0.2.0,  9.12.2018, Martin Mikala, change to three buttons version
# v0.2.1, 23.12.2018, Martin Mikala, chnage rewind to slow revert seek
# v0.2.2, 30.12.2018, martin Mikala, add check and exception for dbus
# v0.2.333, 30.12.2018, martin Mikala, add check and exception for dbus

import omxplayer.player
import omxplayer.keys
from pathlib import Path
from gpiozero import Button
import time
from os import system

time_jump = 0.1
time_current = time.clock_gettime(0) 
time_last = time_current

VIDEO_DIR = "/home/pi/"
VIDEO_FILE = "qq1.mp4"
VIDEO_PATH = Path(VIDEO_DIR + VIDEO_FILE)

buttonP = Button(26)    # button for pause/start
buttonF = Button(13)    # button forward
buttonR = Button(19)    # button rewind back

while True:
		try:
			player = omxplayer.player.OMXPlayer(VIDEO_PATH,dbus_name='org.mpris.MediaPlayer2.omxplayer1',args='--loop')
		

		while not player.can_control():
			print("Can control %s " % player.can_control())
			sleep(0.1)

		#print("Start player status %s" % player.playback_status())

		pushP = False
		lastP = pushP
		pushR = False
		lastR = pushR
		pushF = False
		lastF = pushF

		rewind = False
		forward = False

		player.action(omxplayer.keys.SHOW_INFO)

		while player.can_control():
			time_current = time.clock_gettime(0)
			if time_current - time_last > time_jump:
				#print("last %f curr %f jump %f minus %f" % (time_last,time_current,time_jump,(time_current - time_last)))
				time_last = time_current
				pushP = buttonP.is_pressed
				pushR = buttonR.is_pressed
				pushF = buttonF.is_pressed
			
				if pushP != lastP:             #chanche Play/Pause button
					#print("buttonP")
					#print("player status 1 %s" % player.playback_status())
					if pushP:					# button pushed
						player.pause()		# change mode to pause
					else:						# button released
						player.play()		# change mode to play

					#print("player status 2 %s" % player.playback_status())
					lastP = pushP				# note button state
			
				if pushF != lastF :				#change FF button
					#print("buttonF")
					#print("player status 1 %s" % player.position())
					if pushF:					# button pushed
						player.set_rate(4)
						#forward = True
					else:
						player.set_rate(1)
						#forward = False

					#print("player status 2 %s" % player.position())
					lastF = pushF			#note button state
			
				if pushR != lastR:              #change FF button
					#print("buttonR")
					#print("player status 1 %s" % player.position())
					if pushR:                   # button pushed
						rewind = True
						#player.seek(-1)
					else:
						rewind = False

					#print("player status 2 %s" % player.position())
					lastR = pushR           #note button state

				if rewind:
					player.seek(-0.2)

				if forward:
					player.seek(0.1)

				#print("player position %s , rate %d " % (player.position(), player.rate()))
					
player.quit()
print("End")

