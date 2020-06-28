#!/bin/bash

# zip2lha.sh - convert zip files (for WHDLOAD) into lha for retropie / amiberry
# USAGE: zip2lha.sh zipfilename.zip
# or to do whole directory: find . -name '*.zip -exec zip2lha.sh {} \;
# set TMPDIR & DESTDIR in script
# REQUIREMENTS: unzip & jlha-utils (NOT lha package) on raspbian
# BE CAREFUL! This script removes contents of TMPDIR after each conversion

set -eo

FN=$1
LHAFN=$(echo $FN |sed -e 's/.zip/.lha/')
TMPDIR=/data/tmp
ORIGDIR=$PWD

if [[ ! -f "$FN" ]]; then
    echo "$FN doesn't exit"
    exit
fi

if [[ ! -d "$TMPDIR" ]]; then
    echo "$TMPDIR doesn't exit"
    exit
fi

echo "Extracting $FN to $LHAFN"

unzip -d $TMPDIR "$FN" > /dev/null

cd $TMPDIR || exit
jlha -ao5 "$ORIGDIR/$LHAFN" * > /dev/null
rm -r *
rm "$ORIGDIR/$FN"

