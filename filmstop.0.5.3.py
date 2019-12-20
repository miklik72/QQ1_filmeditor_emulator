#!/usr/bin/env python3

# v0.1.0, 15.11.2018, Martin Mikala, initial version
# v0.1.1, 25.11.2018, Martin Mikala, set path to video as path type 
# v0.2.0,  9.12.2018, Martin Mikala, change to three buttons version
# v0.2.1, 23.12.2018, Martin Mikala, chnage rewind to slow revert seek
# v0.2.2, 30.12.2018, Martin Mikala, possible push only one button
# v0.3.0, 31.01.2019, Martin Mikala, use video with reverse part for rewind back
# v0.3.1, 01.02.2019, Martin Mikala, add debug parameter and fix key colision
# v0.3.2, 11.02.2019, Martin Mikala, don't loop video with fast moving and improve problems with rewind
# v0.3.3, 13.02.2019, Martin Mikala, add loop back, add pause for rewind from start of video
# v0.4.0, 26.03.2019, Martin Mikala, add stop points with show picture
# v0.4.1, 27.03.2019, Martin Mikala, read stop point from file name
# v0.4.2, 28.03.2019, Martin Mikala, hide/show video during pause
# v0.5.0, 16.04.2019, Martin Mikala, load action picture earlier
# v0.5.1, 29.04.2019, Martin Mikala, stop old fbi processes
# v0.5.2, 03.07.2019, Martin Mikala, redirect fbi output to /dev/null and stop logging

import omxplayer.player
import omxplayer.keys
from pathlib import Path
from gpiozero import Button
import time
from os import system,scandir,path
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
time_button_reset = 60
time_last_reset = time_current

VIDEO_DIR = "/home/pi/"
VIDEO_FILE = "qq1.mp4"
VIDEO_PATH = Path(VIDEO_DIR + VIDEO_FILE)
PICTURE_DIR = "/home/pi/"
PICTURE_FILE_PRF = "ok"
PICTURE_FILE_EXT = ".png"
#videoActions_arr = [8,21,40,52,72,87]
videoActions_arr = []
#PICTURE_COUNT = 0
actionTolerance = 0.5


buttonP = Button(26)    # button for pause/start
buttonF = Button(13)    # button forward
buttonR = Button(19)    # button rewind back

#get list of action points and related pictures
files = [f.path for f in scandir(VIDEO_DIR) if f.name.startswith(PICTURE_FILE_PRF)]
for fpath in files:
	fname = path.basename(fpath)
	ftime = fname[2:-4]
	if debug:
		print(fname)
		print(ftime)
	videoActions_arr.append([int(ftime), fpath])
	#PICTURE_COUNT +=1

videoActions_arr.sort()
#PICTURE_COUNT -=1

if debug:
	print("videoActions: {}".format(videoActions_arr))
	#print("pictures count: {}".format(PICTURE_COUNT))

#time.sleep(5)

#while True:
#player = omxplayer.player.OMXPlayer(VIDEO_PATH,dbus_name='org.mpris.MediaPlayer2.omxplayer1',args='--loop')
#player = omxplayer.player.OMXPlayer(VIDEO_PATH,dbus_name='org.mpris.MediaPlayer2.omxplayer1',args='-b --no-osd --loop')
player = omxplayer.player.OMXPlayer(VIDEO_PATH,dbus_name='org.mpris.MediaPlayer2.omxplayer1',args='--no-osd --loop')

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
pauseR = False
pushF = False  # status push forward button
lastF = pushF
activeF = False
pushA = True   # acceppt pusing any button 

rewind = False
forward = False
#duration = player.duration()
duration = 187 
position = 0

pictureIndex = 0

#video_position = 0
#next_position = 0
#next_index = 0
#next_picture = ''


#get right number of picture by position
def get_action_index(videoPosition):
	actionIndex = -1
	for a in videoActions_arr:
		actionIndex +=1
		actionTime = float(a[0]/100 + actionTolerance)
		if videoPosition < actionTime:
			return actionIndex
	return actionIndex 
		

#print("actionIndex {}".format(get_action_index(8000)))
	


# load picture before action
def load_picture(index):
	pictureFile = videoActions_arr[index][1]
	system("sudo killall fbi")
	#system("sudo fbi -T 1 -noverbose %s" % pictureFile)
	system("sudo fbi -T 1 -noverbose %s > /dev/null 2>&1" % pictureFile )
	#	load_bol = False
	if debug:
		print("load picture: {}".format(pictureFile))

def dbus_state():
	#print("dbus state start")
	try:
		player
	except NameError:
		print("player not exists")
	else:
		print("player exists")
	#print("can control  %s" % player.can_control())
	#print("can pause %s" % player.can_pause())
	#print("can play %s" % player.can_play())
	#print("can seek %s" % player.can_seek())
	#print("is playing %s" % player.is_playing())
	#print("dbus state end")

if debug:
	dbus_state()

load_picture(pictureIndex)

while player.can_control():
	time_current = time.clock_gettime(0)
	if time_current - time_last_reset > time_button_reset:
		laspP = False
		lastF = False
		lastR = False
		activeP = False
		activeF = False
		activeR = False
		time_last_reset = time_current 
		if debug:
			print("buttons reset")

	if time_current - time_last > time_jump:
		#if debug:
		#	print("last %f curr %f jump %f minus %f" % (time_last,time_current,time_jump,(time_current - time_last)))
		time_last = time_current
		pushP = buttonP.is_pressed
		pushR = buttonR.is_pressed
		pushF = buttonF.is_pressed
		
		#preload next picture
		videoPosition = player.position()
		actionIndex = get_action_index(videoPosition)
		if actionIndex != pictureIndex and not activeR:
			pictureIndex = actionIndex
			load_picture(pictureIndex)

		#load_picture(videoPosition)


		if pushP != lastP:             #chanche Play/Pause button
			if debug:
				print("button P changed")
				print("pushP %s, lastP %s, activeP %s" % (pushP,lastP,activeP))
				print("player status 1 %s" % player.playback_status())
				print("player position %f" % player.position())
			if  not (activeP or activeF or activeR):					# any button pushed
				if debug:
					dbus_state()
				player.pause()		# change mode to pause
				#pushA = False
				activeP = True
				if debug:
					print("button P active")
					print("pushP %s, lastP %s, activeP %s" % (pushP,lastP,activeP))
				VIDEO_POSITION = player.position()
				for A in videoActions_arr:         # check all action points
					DELTA = abs(VIDEO_POSITION - float(A[0]/100))
					if debug:
						print("position %f, action %f" % (player.position(), A[0]/100))
					if DELTA <= actionTolerance:
						if debug:
							print("Catch action point, position {}, file {}".format(player.position(),A[1]))
						
						#system('fim -q -A -c "sleep 1; quit" smiley_ok2.png')
						#system('fim -q -A -c "sleep 1; quit" ok800.png')
						#system("fim -q -A -c 'quit' %s" % A[1])
						#system("sudo fbi -T 1 -noverbose %s" % A[1])
						player.hide_video()
						break

			elif activeP:				# button released
				if debug:
					dbus_state()
				player.show_video()
				#player.set_alpha(255)
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
				#if newposition > duration - 1:
					#newposition = duration - 2
				if debug:
					print("button R active")
					print("pushR %s, lastR %s, activeR %s, newposition %f" % (pushR,lastR,activeR,newposition))
					print("player position A1 %f" % player.position())
					dbus_state()
				if position > 2:
					pauseR = False
					if debug:
						print("go to newposition for rewind, pauseR %s" % pauseR)
					player.set_position(newposition)
					#if not player.is_playing():
					#	if debug:
					#		print("R wait 1s, is playing %s" % player.is_playing())
					#		time.sleep(1)
				else:
					pauseR = True
					if debug:
						print("pause for rewind, pauseR %s" % pauseR)
					player.pause()
				time.sleep(0.5)
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
				#if newposition < 1:
				#	newposition = 1
				if debug:
					print("button R inactive, pauseR %s" % pauseR)
					print("pushR %s, lastR %s, activeR %s, newposition %f" % (pushR,lastR,activeR,newposition))
					print("player position I1 %f" % player.position())
					dbus_state()
				if not pauseR:
					player.set_position(newposition)
					time.sleep(0.5)
				if debug:
					print("player position I2 %f" % player.position())
					print("player playing I2 %s %s" % (player.is_playing(),time.clock_gettime(0)))
				if not player.is_playing():
					print("start play after rewind")
					#time.sleep(0.2)
					player.play()
					if not player.is_playing():
						print("F wait 1s")
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
		next_index = 0
		next_picture = ''

	# go backward only to end of video and then go to half where startin reverse part
	if activeR == True and player.position() > duration-1:
		if player.is_playing():
			player.pause()
			if debug:
				print("rewert, pause in the end")
				dbus_state()

	
player.quit()
print("End")

# vim: noexpandtab tabstop=4

