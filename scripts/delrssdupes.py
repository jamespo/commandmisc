#!/bin/env python3

# delrssdupes.py - remove duplicates from RSS file
# Takes RSS on stdin and outputs clean version on stdout

from collections import Counter
import re
import sys

in_item = False
seen_titles = Counter()
buffer = ''
title = None

for line in sys.stdin:
    if re.match(r' *<item>', line):
        in_item = True
        buffer += line
    elif in_item and (titlematch := re.search(r' *<title>(.*)</title>', line)):
        title = titlematch.group(1)
        seen_titles.update({title: 1})
        buffer += line
    elif re.match(r' *</item>', line):
        buffer += line
        if seen_titles[title] == 1:
            print(buffer, end='')
        buffer = ''
        title = None
        in_item = False
    elif not in_item:
        print(line, end='')
    else:
        # in_item
        buffer += line
