#!/bin/bash

export DBUS_SESSION_BUS_PID=`cat "/tmp/omxplayerdbus.${USER:-pi}.pid"`
export DBUS_SESSION_BUS_ADDRESS=`cat "/tmp/omxplayerdbus.${USER:-pi}"`
dbus-send --print-reply --session --dest=org.mpris.MediaPlayer2.omxplayer1 /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.Action int32:15
