#!/usr/bin/env python3

# teleprinter.py - teleprint an updating webpage, eg BBC Wimbledon
# live commentary

import requests
import sys




def slowscroll(text, speed=0.05):
    for char in text:
        sys.stdout.write('%s' % char)
        sys.stdout.flush()
        time.sleep(speed)


def main(url):
    page = requests.get(url)


if __name__ == '__main__':
    try:
        main(sys.argv[1])
    except IndexError:
        print('USAGE: teleprinter.py URL')
        
