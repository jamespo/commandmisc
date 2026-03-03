#!/bin/bash

# pluggedin.sh - USAGE: pluggedin.sh [-p|-n] [executable]
# return 0 if plugged in, 1 otherwise
# if argument supplied run it

UPOWERPATH=/org/freedesktop/UPower/devices/line_power_ADP0

pluggedin=$(upower -i $UPOWERPATH | grep -P 'online.*yes')

if [[ -n "$1" ]]; then
    if [[ "$1" = "-n" ]]; then
	pluggedin_mode="notpluggedin"
    elif [[ "$1" = "-p" ]]; then
	pluggedin_mode="pluggedin"
    else
	pluggedin_mode="whocares"
    fi
    pluggedin_exe="$2"
fi

if [[ -n "$pluggedin" ]]; then
    # it's plugged in
    if [[ $pluggedin_mode = "pluggedin" ]]; then
	$pluggedin_exe
    fi

    exit 0
else
    if [[ $pluggedin_mode = "notpluggedin" ]]; then
	$pluggedin_exe
    fi

    exit 1
fi
