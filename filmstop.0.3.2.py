#!/usr/bin/env python3

# v0.1.0, 15.11.2018, Martin Mikala, initial version
# v0.1.1, 25.11.2018, Martin Mikala, set path to video as path type 
# v0.2.0,  9.12.2018, Martin Mikala, change to three buttons version
# v0.2.1, 23.12.2018, Martin Mikala, chnage rewind to slow revert seek
# v0.2.2, 30.12.2018, Martin Mikala, possible push only one button
# v0.3.0, 31.01.2019, Martin Mikala, use video with reverse part for rewind back
# v0.3.1, 01.02.2019, Martin Mikala, add debug parameter and fix key colision
# v0.3.2, 11.02.2019, Martin Mikala, don't loop video with fast moving and improve problems with rewind

import omxplayer.player
import omxplayer.keys
from pathlib import Path
from gpiozero import Button
import time
from os import system
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-d","--debug",action="store_true",help="print debug info")
args = parser.parse_args()
debug = args.debug

if debug:
	print("Debug")

time_jump = 0.5
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

if debug:
	print("Start player status %s" % player.playback_status())

pushP = False  # status push pause button
lastP = pushP
activeP = False
pushR = False  # status push rewind button
lastR = pushR
activeR = False
pushF = False  # status push forward button
lastF = pushF
activeF = False
pushA = True   # acceppt pusing any button 

rewind = False
forward = False
duration = player.duration()
position = 0

#player.action(omxplayer.keys.SHOW_INFO)

def dbus_state():
	print("dbus state start")
	try:
		player
	except NameError:
		print("player not exists")
	else:
		print("player exists")
	print("can control  %s" % player.can_control())
	print("can pause %s" % player.can_pause())
	print("can play %s" % player.can_play())
	print("can seek %s" % player.can_seek())
	print("is playing %s" % player.is_playing())
	print("dbus state end")

if debug:
	dbus_state()

while player.can_control():
	time_current = time.clock_gettime(0)
	if time_current - time_last > time_jump:
		#if debug:
		#	print("last %f curr %f jump %f minus %f" % (time_last,time_current,time_jump,(time_current - time_last)))
		time_last = time_current
		pushP = buttonP.is_pressed
		pushR = buttonR.is_pressed
		pushF = buttonF.is_pressed
		
		if pushP != lastP:             #chanche Play/Pause button
			if debug:
				print("button P changed")
				print("pushP %s, lastP %s, activeP %s" % (pushP,lastP,activeP))
				print("player status 1 %s" % player.playback_status())
			if  not (activeP or activeF or activeR):					# any button pushed
				if debug:
					dbus_state()
				player.pause()		# change mode to pause
				#pushA = False
				activeP = True
				if debug:
					print("button P active")
					print("pushP %s, lastP %s, activeP %s" % (pushP,lastP,activeP))
			elif activeP:				# button released
				if debug:
					dbus_state()
				player.play()		# change mode to play
				#pushA = True
				activeP = False
				if debug:
					print("button P inactive")
					print("pushP %s, lastP %s, activeP %s" % (pushP,lastP,activeP))
					print("player status 2 %s" % player.playback_status())
			lastP = pushP				# note button state
	
		if pushF != lastF:				#change FF button
			if debug:
				print("button F changed")
				print("pushF %s, lastF %s, activeF %s" % (pushF,lastF,activeF))
				print("player position %f" % player.position())
			if  not (activeP or activeF or activeR):					# any button pushed
				if debug:
					dbus_state()
				player.set_rate(4)
				#pushA = False
				activeF = True
				if debug:
					print("button F active")
					print("pushF %s, lastF %s, activeF %s" % (pushF,lastF,activeF))
					print("player position A %f" % player.position())
			elif activeF:
				if debug:
					dbus_state()
				player.set_rate(1)
				#pushA = True
				activeF = False
				if debug:
					print("button F inactive")
					print("pushF %s, lastF %s, activeF %s" % (pushF,lastF,activeF))
					print("player position I %f" % player.position())
			lastF = pushF			#note button state
	
		if pushR != lastR:              #change RB button
			if debug:
				print("buttonR")
				print("pushR %s, lastR %s, activeR %s" % (pushR,lastR,activeR))
				print("player position %f" % player.position())
			if  not (activeP or activeF or activeR):                    # any button pushed	
				#rewind = True
				#pushA = False
				activeR = True
				#player.seek(-1)
				if debug:
					dbus_state()
				position = player.position()
				newposition = duration - position 
				if newposition > duration - 1:
					newposition = duration - 2
				if debug:
					print("button R active")
					print("pushR %s, lastR %s, activeR %s, newposition %f" % (pushR,lastR,activeR,newposition))
					print("player position A1 %f" % player.position())
					dbus_state()

				player.set_position(newposition)
				if debug:
					dbus_state()
					print("player position A2 %f" % player.position())
				#player.set_rate(4)
			elif activeR:                   
				#rewind = False
				pushA = True
				activeR = False
				#player.set_rate(1)
				position = player.position()
				newposition = duration - position
				if newposition < 1:
					newposition = 1
				if debug:
					print("button R inactive")
					print("pushR %s, lastR %s, activeR %s, newposition %f" % (pushR,lastR,activeR,newposition))
					print("player position I1 %f" % player.position())
					dbus_state()
				player.set_position(newposition)
				if debug:
					print("player position I2 %f" % player.position())
					print("player playing I2 %s %s" % (player.is_playing(),time.clock_gettime(0)))
				if not player.is_playing():
					print("start play after rewind")
					time.sleep(0.2)
					player.play()
					if not player.is_playing():
						print("wait 1s")
						time.sleep(1)
						player.play()
					print("player playing  I3 %s %s" % (player.is_playing(),time.clock_gettime(0)))

				if debug:
					print("button R inactive")
					print("pushR %s, lastR %s, activeR %s, newposition %f" % (pushR,lastR,activeR,newposition))
					print("player position I3 %f" % player.position())
			lastR = pushR           #note button state

	# go forward only to half of video, that go to start
	if activeR == False and player.position() > duration/2-1:
		if debug:
			print("forward in the midle go to start")
			dbus_state()
		player.set_position(0)

	# go backward only to end of video and then go to half where startin reverse part
	if activeR == True and player.position() > duration-1:
		if player.is_playing():
			player.pause()
			if debug:
				print("rewert, pause in the end")
				dbus_state()

	
player.quit()
print("End")

# vim: noexpandtab
