#!/bin/bash

# check-systemd-socket.sh - restart failed systemd socket units
# USAGE: check-systemd-socket.sh [SOCKETNAME]

DELAY=60
SERVICENAME=$1
SERVICE="${SERVICENAME}.socket"
SKIPFILE="/tmp/dont_restart_${SERVICENAME}"
LOGFILE="/var/log/check-systemd-socket-${SERVICENAME}.log"

touch $LOGFILE
chmod 755 $LOGFILE


logline () {
    DATE=$(date)
    echo "$DATE $1"
}

logline "Starting $SERVICENAME"

while true
do      
    sleep $DELAY

    failed=$(systemctl is-failed $SERVICE)
    failedrc=$?

    if [[ $failedrc -eq 0 ]]; then
	# failed
	if [[ ! -f $SKIPFILE ]]; then
	    logline "Restarting $SERVICE"
	    systemctl restart $SERVICE
	fi
    fi
done
