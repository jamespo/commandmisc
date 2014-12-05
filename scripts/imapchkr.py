#!/usr/bin/env python

# imapchkr.py - checks for new messages in IMAP server
# (c) James Powell - jamespo [at] gmail [dot] com 2014
# Create ~/.config/.imapchkr.conf with contents
# [Main]
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
    mail = imaplib.IMAP4_SSL(server)
    mail.login(user, pw)
    mail.list()
    mail.select(folder) # connect to inbox.
    (retcode, messages) = mail.search(None, '(UNSEEN)')
    if retcode == 'OK':
        if messages[0] == '':
            return 0
        else:
            return len(messages[0].split(' '))
    else:
        return 0

def main():
    config = readconf()
    user, pw, server = (config.get('Main', 'user'), config.get('Main', 'password'),
                        config.get('Main', 'server'))
    print checknew(user, pw, server)


if __name__ == '__main__':
    main()
