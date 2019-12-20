#!/usr/bin/env python3

# v0.1.0, 15.11.2018, Martin Mikala, initial version
# v0.1.1, 25.11.2018, Martin Mikala, set path to video as path type 
# v0.2.0,  9.12.2018, Martin Mikala, change to three buttons version
# v0.2.1, 23.12.2018, Martin Mikala, chnage rewind to slow revert seek
# v0.2.2, 30.12.2018, Martin Mikala, possible push only one button
# v0.3.0, 31.01.2019, Martin Mikala, use video with reverse part for rewind back

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
VIDEO_FILE = "qq1cr.mkv"
VIDEO_PATH = Path(VIDEO_DIR + VIDEO_FILE)

buttonP = Button(26)    # button for pause/start
buttonF = Button(13)    # button forward
buttonR = Button(19)    # button rewind back

#time.sleep(5)

#while True:
#player = omxplayer.player.OMXPlayer(VIDEO_PATH,dbus_name='org.mpris.MediaPlayer2.omxplayer1',args='--loop')
player = omxplayer.player.OMXPlayer(VIDEO_PATH,dbus_name='org.mpris.MediaPlayer2.omxplayer1',args='-b --no-osd ')

while not player.can_control():
	print("Can control %s " % player.can_control())
	sleep(0.1)

#print("Start player status %s" % player.playback_status())

pushP = False  # status push pause button
lastP = pushP
pushR = False  # status push rewind button
lastR = pushR
pushF = False  # status push forward button
lastF = pushF
pushA = True   # acceppt pusing any button 

rewind = False
forward = False
duration = player.duration()
position = 0

#player.action(omxplayer.keys.SHOW_INFO)

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
			if pushP and pushA:					# button pushed
				player.pause()		# change mode to pause
				pushA = False
			else:						# button released
				player.play()		# change mode to play
				pushA = True
				#print("player status 2 %s" % player.playback_status())
			lastP = pushP				# note button state
	
		if pushF != lastF:				#change FF button
			#print("buttonF")
			#print("player status 1 %s" % player.position())
			if pushF and pushA:					# button pushed
				player.set_rate(4)
				pushA = False
				#forward = True
			else:
				player.set_rate(1)
				pushA = True
				#forward = False
				#print("player status 2 %s" % player.position())
			lastF = pushF			#note button state
	
		if pushR != lastR:              #change RB button
			#print("buttonR")
			#print("player status 1 %s" % player.position())
			if pushR and pushA:                   # button pushed
				rewind = True
				pushA = False
				#player.seek(-1)
				position = player.position()
				newposition = duration - position 
				player.set_position(newposition)
				#player.set_rate(4)
			else:
				rewind = False
				pushA = True
				#player.set_rate(1)
				position = player.position()
				newposition = duration - position
				player.set_position(newposition)
				#print("player status 2 %s" % player.position())
			lastR = pushR           #note button state

		#if rewind:
			#player.seek(-0.2)

		#if forward:
			#player.seek(0.1)

		#print("player position %s , rate %d " % (player.position(), player.rate()))
					
	# go forward only to half of dideo, that go to start
	if rewind == False and player.position() > duration/2-1:
		player.set_position(0)

	# go backward only to end of video and then go to half where startin reverse part
	if rewind == True and player.position() > duration-1:
		player.set_position(duration/2)
		

player.quit()
print("End")

