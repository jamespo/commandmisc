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
#from optparse import OptionParser
import ConfigParser
import Queue
import threading

#def getopts():
#    parser = OptionParser()
#    parser.add_option("-s", help="search string", action="store", dest="txt")

def readconf():
    config = ConfigParser.ConfigParser()
    config.read(os.path.expanduser('~/.config/.imapchkr.conf'))
    return config

def checknew(q, account, user, pw, server, folder="INBOX"):
    '''returns tuple of account, unread, total # of messages'''
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
    else:
        q.put((account, None, None))

def format_msgcnt(server, new_msg, all_msg):
    return '[%s: %d/%d]' % (server, new_msg, all_msg)

def main():
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
        counts.append(format_msgcnt(*msg_results))
    print ' '.join(counts)

if __name__ == '__main__':
    main()
