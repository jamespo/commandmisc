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

#def getopts():
#    parser = OptionParser()
#    parser.add_option("-s", help="search string", action="store", dest="txt")

def readconf():
    config = ConfigParser.ConfigParser()
    config.read(os.path.expanduser('~/.config/.imapchkr.conf'))
    return config

def checknew(user, pw, server, folder="INBOX"):
    '''returns tuple of unread, total # of messages'''
    mail = imaplib.IMAP4_SSL(server)
    mail.login(user, pw)
    mail.list()
    (allretcode, allmessages_str) = mail.select(folder) # connect to inbox.
    (unretcode, unmessages) = mail.search(None, '(UNSEEN)')
    if (unretcode, allretcode) == ('OK', 'OK'):
        allmessages_num = int(allmessages_str[0])
        if unmessages[0] == '':
            return (0, allmessages_num)
        else:
            return (len(unmessages[0].split(' ')), allmessages_num)
    else:
        return (None, None)

def format_msgcnt(server, new_msg, all_msg):
    return '[%s: %d/%d]' % (server, new_msg, all_msg)

def main():
    config = readconf()
    counts = []
    for srv_sect in config.sections():
        user, pw, server = (config.get(srv_sect, 'user'), config.get(srv_sect, 'password'),
                            config.get(srv_sect, 'server'))
        msg_count = checknew(user, pw, server)
        counts.append(format_msgcnt(srv_sect, *msg_count))
    print ' '.join(counts)

if __name__ == '__main__':
    main()
