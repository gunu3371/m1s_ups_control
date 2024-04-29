#!/bin/bash
UPS_TTY_NODE=""
VID_CH55xduino="1209"
PID_CH55xduino="C550"
function find_tty_node {
	UPS_TTY_NODE=`find $(grep -l "PRODUCT=$(printf "%x/%x" "0x${VID_CH55xduino}" "0x${PID_CH55xduino}")" \
					/sys/bus/usb/devices/[0-9]*:*/uevent | sed 's,uevent$,,') \
					/dev/null -name dev -o -name dev_id  | sed 's,[^/]*$,uevent,' |
					xargs sed -n -e s,DEVNAME=,/dev/,p -e s,INTERFACE=,,p`

}

function kill_dead_process {
	PID=""
	PID=`ps -eaf | grep ${UPS_TTY_NODE} | grep -v grep | awk '{print $2}'`
	if [ -n "$PID" ]; then
		kill -9 $PID
	fi
}

find_tty_node

kill_dead_process

echo ${UPS_TTY_NODE}