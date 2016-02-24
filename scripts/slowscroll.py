#!/usr/bin/env python

# slowscroll.py - scroll a given text file sloooowly

import sys
import time

speed = 0.05
if len(sys.argv) >= 3:
    speed = float(sys.argv[2])
if len(sys.argv) >= 2:
    slowfile = sys.argv[1]
else:
    slowfile = sys.stdin
    
with open(slowfile) as f:
    while True:
        char = f.read(1)
        if char:
            sys.stdout.write('%s' % char)
            sys.stdout.flush()
            time.sleep(speed)
        else:
            break
    
