#!/usr/bin/env python

# slowscroll.py - scroll a given text file sloooowly

import sys
import time

speed = 0.05
if len(sys.argv) >= 3:
    speed = float(sys.argv[2])

with open(sys.argv[1]) as f:
    while True:
        char = f.read(1)
        if char:
            sys.stdout.write('%s' % char)
            sys.stdout.flush()
            time.sleep(speed)
        else:
            break
    
