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
# v0.5.3, 25.07.2019, Martin Mikala, reset button status every minute
# v0.6.0, 25.07.2019, Martin Mikala, new buttons control

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

if debug: print("Debug")

time_debounce = 0.1
time_action = 0.5
time_current = time.clock_gettime(0) 
time_last_button = time_current
time_last_action= time_current
action =  "play"
action_last = "pause"

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

#player = omxplayer.player.OMXPlayer(VIDEO_PATH,dbus_name='org.mpris.MediaPlayer2.omxplayer1',args='--loop')
#player = omxplayer.player.OMXPlayer(VIDEO_PATH,dbus_name='org.mpris.MediaPlayer2.omxplayer1',args='-b --no-osd --loop')
player = omxplayer.player.OMXPlayer(VIDEO_PATH,dbus_name='org.mpris.MediaPlayer2.omxplayer1',args='--no-osd --loop')

while not player.can_control():
	print("Can control {}".format(player.can_control()))
	time.sleep(0.1)

if debug: print("Start player status {}".format(player.playback_status()))

#duration = player.duration()
duration = 187 
position = 0
pictureIndex = 0

#get right number of picture by position
def get_action_index(videoPosition):
	actionIndex = -1
	for a in videoActions_arr:
		actionIndex +=1
		actionTime = float(a[0]/100 + actionTolerance)
		if videoPosition < actionTime:
			return actionIndex
	return actionIndex 
		
# load picture before action
def load_picture(index):
	pictureFile = videoActions_arr[index][1]
	system("sudo killall fbi")
	#system("sudo fbi -T 1 -noverbose %s" % pictureFile)
	system("sudo fbi -T 1 -noverbose %s > /dev/null 2>&1" % pictureFile )
	#	load_bol = False
	if debug: print("load picture: {}".format(pictureFile))

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

def control_buttons():
	global time_last_button
	#check only every 0.1s
	_time_current = time.clock_gettime(0)
	if _time_current - time_last_button > time_debounce:
		time_last_button = _time_current
		_pushP = buttonP.is_pressed
		_pushR = buttonR.is_pressed
		_pushF = buttonF.is_pressed
		#only one button will be active
		if _pushP:
			_action = "pause"
		elif _pushF:
			_action = "forward"
		elif _pushR:
			_action = "rewind"
		else:
			_action = "play"
		return _action
	else:
		return "noop"

def switch_direction():
	if not player.is_playing():
		player.play()
		if debug: print("SWITCH play set in the start")
	position = player.position()
	newposition = duration - position	# new position in 2nd part
	if debug: print("switch direction position {}, newposition {}".format(position,newposition))
	if position < duration/2:
		if debug: print("go to newposition for rewind")
	else:
		if debug: print("go to newposition for forvard")
	player.set_position(newposition)
	while not player.is_playing():
		time.sleep(0.01)
		if debug: print("SWITCH wait for play, status {}".format(player.playback_status()))

if debug:
	dbus_state()

load_picture(pictureIndex)
		
while player.can_control():
	#preload next picture
	videoPosition = player.position()
	actionIndex = get_action_index(videoPosition)
	if actionIndex != pictureIndex and not action in ["rewind","noop"]:
		pictureIndex = actionIndex
		load_picture(pictureIndex)
		if debug:
			print("load new picture with index {}, action {}".format(pictureIndex,action))

	action = control_buttons()
	time_current = time.clock_gettime(0)
	if time_current - time_last_action > time_action and action != "noop":   #change action every 0.5s
		if action != action_last:						#only if action changed
			
			if debug:
				print("start action >>> {}, last action >>> {}".format(action,action_last))
				print("player status {}".format(player.playback_status()))
				print("player position {}".format(player.position()))

			if action_last == "rewind":
				switch_direction()

				if debug: print("switch direction and play after rewind, status {}".format(player.playback_status()))

			elif action_last == "forward":
				player.set_rate(1)
				if debug: print("set rate 1, after FF")

			elif action_last == "pause":
				player.show_video()
				if debug: print("show video after pause")
			

			if action == "pause":
				player.pause()		# change mode to pause

				#check action points
				VIDEO_POSITION = player.position()
				for A in videoActions_arr:         # check all action points
					DELTA = abs(VIDEO_POSITION - float(A[0]/100))
					if debug: print("position {}, action {}".format(player.position(), A[0]/100))
					if DELTA <= actionTolerance:
						if debug: print("Catch action point, position {}, file {}".format(player.position(),A[1]))
						
						player.hide_video()
						break		# escape from loop

			elif action == "forward":
				player.set_rate(4)
				if debug: print("FF start set rate 4") 

			elif action == "rewind":
				switch_direction()
				if debug: print("RWD start: {}".format(player.playback_status()))
			
			elif action == "play":
				player.play()
				if debug: print("PLAY start")

			elif action == "noop":
				pass
				if debug: print("NOOP start")

			else:
				pass

			action_last = action       #move to end

	# go forward only to half of video, that go to start
	if action in ["play", "forward"] and player.position() > duration/2-1:
		if debug: print("forward in the midle go to start")
		player.set_position(0)
		next_index = 0
		next_picture = ''

	# go backward only to end of video and then go to half where startin reverse part
	if action in ["rewind"] and player.position() > duration-1:
		if player.is_playing():
			player.pause()
			if debug:
				print("rewert, pause in the end")
				dbus_state()

	
player.quit()
print("End")

# vim: noexpandtab tabstop=4

