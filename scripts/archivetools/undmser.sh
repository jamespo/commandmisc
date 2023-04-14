#!/bin/bash

# undmser.sh - batch convert amiga DMS files to ADF
# removes DMS file if successful
#
# run with find . -iname '*.dms' -exec undmser.sh {} \;

DMSPATH="$1"
DMSDIR=$(dirname "$DMSPATH")
DMSFILE=$(basename "$DMSPATH")

echo $DMSPATH

cd "$DMSDIR" || exit
xdms u "$DMSFILE" && rm "$DMSFILE"
