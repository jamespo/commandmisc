#!/bin/env python3

# quickly remove part of a filename

import os
import sys

try:
    remove_path = sys.argv[1]
    assert len(remove_path) > 0
except (IndexError, AssertionError):
    print('USAGE: quickrename.py [part of filename to remove]')
    sys.exit(1)

allobj = os.scandir(os.getcwd())

for entry in allobj:
    if entry.is_file() and remove_path in entry.name:
        newname = entry.name.replace(remove_path, '')
        print(entry.name, newname)
        if not os.getenv('QRDRYRUN'):
                os.rename(entry.name, newname)
