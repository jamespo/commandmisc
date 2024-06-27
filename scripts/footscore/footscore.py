#!/bin/env python3

import argparse
import datetime
import json
import logging
import os
import os.path
import requests
import time

logging.basicConfig()
logger = logging.getLogger()

def getargs():
    '''get CLI args'''
    current_date = datetime.date.today().strftime(format='%Y-%m-%d')
    parser = argparse.ArgumentParser(description='Get Football Scores')
    parser.add_argument('--date', default=current_date,
                        help='date (default: current %s)' % current_date)
    parser.add_argument('--ttl', default=60, type=int,
                        help='cache TTL in seconds (default: 60)')
    return parser.parse_args()


def load_cache(cachepath, ttl):
    cache_mtime = int(os.stat(cachepath).st_mtime)
    now = int(time.time())
    if (cache_mtime + ttl < now):
        # cache expired
        logger.debug('cache expired')
        return None
    logger.debug(cache_mtime)
    with open(cachepath, 'rb') as cp:
        content = cp.read()
    return content


def save_cache(content, cachepath):
    with open(cachepath, 'wb') as cp:
        cp.write(content)


def main():
    args = getargs()
    cache_path = os.path.expanduser(f"~/.cache/footscore/content_{args.date}.json")
    score_cache = None
    if os.path.isfile(cache_path):
        logger.debug('loading from cache')
        score_cache = load_cache(cache_path, args.ttl)
    if score_cache is not None:
        score_json = json.loads(score_cache)
    else:
        # cache expired - load fresh
        URL = f"https://web-cdn.api.bbci.co.uk/wc-poll-data/container/sport-data-scores-fixtures?selectedEndDate={args.date}&selectedStartDate={args.date}&todayDate={args.date}&urn=urn%3Abbc%3Asportsdata%3Afootball%3Atournament%3Aeuropean-championship&useSdApi=false"
        logger.debug(URL)
        score_req = requests.get(URL)
        score_json = json.loads(score_req.content)
        save_cache(score_req.content, cache_path)
    logger.debug(score_json)
    try:
        for group in score_json['eventGroups'][0]['secondaryGroups']:
            for event in group['events']:
                score_txt = '%s %s - %s %s' % (event['home']['shortName'],
                                               event['home'].get('scoreUnconfirmed', '_'),
                                               event['away']['shortName'],
                                               event['away'].get('scoreUnconfirmed', '_'))
                print(score_txt)
    except IndexError:
        print('No games today')

if __name__ == '__main__':
    if os.getenv("FPDEBUG"):
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.ERROR)
    main()
