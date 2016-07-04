#!/bin/bash

# cdx.sh - change to dir used by other shell
# (c) 2016 jamespo [at] gmail [dot] com
# INSTALL: define shell function as below:
# cdx ()
# {
#     cd "$(cdx.sh $@)"
# }
# USAGE: cdx

set -eu

# get shell proc PIDs
shell=$(getent passwd $LOGNAME | cut -d: -f7)
pids=$(pidof $shell)

#echo $pids

# get cwds of shell procs
shelldirs=()
for pid in $pids; do
    shelldir=$(pwdx $pid | awk '{ print $2 }')
    shelldirs+=($shelldir)
done
# remove duplicate dirs
uniqdirs=($(printf "%s\n" "${shelldirs[@]}" | sort -u))

prompt="Select dir"

PS3="$prompt: "
select opt in "${uniqdirs[@]}"; do

    echo -n $opt
    break

done
