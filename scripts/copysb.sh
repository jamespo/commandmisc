#!/bin/bash

# copysb.sh - copy python script and change shebang to current virtualenv
# destination path defaults to ~/bin/

set -e

USAGE="copysb.sh script.py [path]"
SCRIPT="$1"
COPYPATH="${2:-$HOME/bin}"

function usage {
    echo "USAGE: $1"
    echo $USAGE
    exit 1
}

# check args
if [[ ! -f $SCRIPT ]]; then
   usage "no script specified"
fi

if [[ ! -f $SCRIPT ]]; then
   usage "no script specified"
fi

#
SHEBANG="#!$(which python)"
cp "$SCRIPT" "$COPYPATH/"
sed -i -e "1s@.*@$SHEBANG@" "$COPYPATH/$SCRIPT"
echo "Copied $SCRIPT to $COPYPATH with $SHEBANG"
