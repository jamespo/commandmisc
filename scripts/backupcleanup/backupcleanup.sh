#!/bin/bash
#
# backupcleanup.sh

USAGE="backupcleanup.sh [DIR] [# recent files to keep]"

BASEDIR=.
MOSTRECENT=5  # add one - so 5 leaves 4 newest files in dir
MINDEPTH=0
MAXDEPTH=0

find "$BASEDIR" -maxdepth $MAXDEPTH -mindepth $MINDEPTH -type d -print0 | while read -d $'\0' subdir
do
    if [[ ! -z "$BCDEBUG" ]]; then
	# just echo
	echo "DIR: $subdir"
	(cd "$subdir" && ls -tp | grep -v '/$' | tail -n +${MOSTRECENT} | xargs -I {} echo rm {})
    else
	echo
	# (cd "$subdir" && ls -tp | grep -v '/$' | tail -n +${MOSTRECENT} | xargs -I {} rm -- {})
    fi
done
