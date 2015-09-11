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
    parser.add_option("-s", help="short output", action="store_true",
                      dest="short", default = False)
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

def format_msgcnt(options, servercount):
    output = ''
    for server, new_msg, all_msg in servercount:
        if options.short:
            output += "%s:%s " % (server[0] , new_msg)
        elif None in (new_msg, all_msg):
            output += '[%s: unknown] ' % server
        elif options.color and new_msg > 0:
            output += '[%s: %s%d/%d%s] ' % (server, colmap['HILIT'],
                                new_msg, all_msg, colmap['NORM'])
        else:
            output += '[%s: %d/%d] ' % (server, new_msg, all_msg)
    output = output.rstrip()
    return output

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
        counts.append(msg_results)
    print format_msgcnt(cmd_options, counts)

if __name__ == '__main__':
    main()
