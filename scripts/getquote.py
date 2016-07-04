#!/usr/bin/env python

# getquote.py - get quote from google
# USAGE: getquote.py LSE:BARC

from __future__ import print_function
import requests
import json
import sys

def main(ticker):
    '''get the quote from google & output it'''
    r = requests.get('http://www.google.com/finance/info?q=%s' % ticker)
    assert r.status_code == 200
    # hack to remove leading comment
    quote_json = r.content.lstrip().lstrip('/')
    results = json.loads(quote_json)[0]
    print('%s: %s (%s%%)' % (results['t'], results['l'], results['cp_fix']),
          end = '')
    
if __name__ == '__main__':
    try:
        main(sys.argv[1])
    except IndexError:
        print('ERROR: must supply ticker code')
        
