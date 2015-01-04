#!/usr/bin/env python

# imapchkr.py - checks for new messages in IMAP server
# (c) James Powell - jamespo [at] gmail [dot] com 2014
# Create ~/.config/.imapchkr.conf with 1 or more sections as below:
# [serveralias]
# user=james
# password=2347923rbkaa
# server=yourimapserver.com

import os
import imaplib
from optparse import OptionParser
import ConfigParser
import Queue
import threading

colmap = {      # shell escape codes
    'NORM'      : '\033[0m',
    'HILIT'     : '\033[37;1m',
}

def getopts():
    parser = OptionParser()
    parser.add_option("-b", help="b/w output", action="store_false",
                      dest="color", default = True)
    (options, args) = parser.parse_args()
    return options

def readconf():
    config = ConfigParser.ConfigParser()
    config.read(os.path.expanduser('~/.config/.imapchkr.conf'))
    return config

def checknew(q, account, user, pw, server, folder="INBOX"):
    '''returns tuple of account, unread, total # of messages'''
    try: 
        mail = imaplib.IMAP4_SSL(server)
        mail.login(user, pw)
        mail.list()
        (allretcode, allmessages_str) = mail.select(folder) # connect to inbox.
        (unretcode, unmessages) = mail.search(None, '(UNSEEN)')
        if (unretcode, allretcode) == ('OK', 'OK'):
            allmessages_num = int(allmessages_str[0])
            if unmessages[0] == '':
                q.put((account, 0, allmessages_num))
            else:
                q.put((account, len(unmessages[0].split(' ')), allmessages_num))
            return
    except:
        pass
    q.put((account, None, None))

def format_msgcnt(color, server, new_msg, all_msg):
    if None in (new_msg, all_msg):
        return '[%s: unknown]' % server
    elif color and new_msg > 0:
        return '[%s: %s%d/%d%s]' % (server, colmap['HILIT'],
                                new_msg, all_msg, colmap['NORM'])
    else:
        return '[%s: %d/%d]' % (server, new_msg, all_msg)


def main():
    cmd_options = getopts()
    config = readconf()
    accounts = config.sections()
    q = Queue.Queue(len(accounts))
    for account in accounts:
        user, pw, server = (config.get(account, 'user'),
                            config.get(account, 'password'),
                            config.get(account, 'server'))
        t = threading.Thread(target=checknew, args = (q, account,
                                                      user, pw, server))
        t.start()
    counts = []
    for account in accounts:
        msg_results = q.get()
        counts.append(format_msgcnt(cmd_options.color, *msg_results))
    print ' '.join(counts)

if __name__ == '__main__':
    main()
