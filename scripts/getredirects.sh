#!/bin/bash

# getredirects.sh - get the redirects from list of urls from STDIN

while read line
do
    redirurl=$(curl -s -I "$line" | grep -o 'http.*')
    echo $redirurl
done < "${1:-/dev/stdin}"
