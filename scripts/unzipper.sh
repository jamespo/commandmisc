#!/bin/bash

# unzipper.sh - batch unzip a recursive directory of zips
# removes zip file if unzip is successful. overwrites by default.
#
# run with find . -name '*.zip' -exec unzipper.sh {} \;

ZIPPATH="$1"
ZIPDIR=$(dirname "$ZIPPATH")

echo $ZIPPATH

unzip -o "$ZIPPATH" -d "$ZIPDIR/" && rm "$ZIPPATH"
