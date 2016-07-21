#!/bin/bash

# emailifoutput.sh

USAGE="emailifoutput.sh command recipient subject"

COMMAND=$1
RECIPIENT=$2
SUBJECT=$3

OUTPUT=$($COMMAND)

if [[ -n "$OUTPUT" ]]; then
    echo "$OUTPUT" | mail -s "$SUBJECT" $RECIPIENT
fi
