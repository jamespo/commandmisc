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
import email
from email.header import decode_header
from optparse import OptionParser
from collections import namedtuple
import ConfigParser
import Queue
import threading

colmap = {      # shell escape codes
    'NORM'      : '\033[0m',
    'HILIT'     : '\033[37;1m',
}


def getopts():
    '''returns OptionParser.options for CL switches'''
    parser = OptionParser()
    parser.add_option("-b", help="b/w output", action="store_false",
                      dest="color", default = True)
    parser.add_option("-s", help="short output", action="store_true",
                      dest="short", default = False)
    parser.add_option("-l", help="list mail summary", action="store_true",
                      dest="listmail", default = False)
    (options, args) = parser.parse_args()
    return options


def readconf():
    '''returns ConfigParser object with account details'''
    config = ConfigParser.ConfigParser()
    config.read(os.path.expanduser('~/.config/.imapchkr.conf'))
    return config


def checknew(q, account, user, pw, server, get_summaries=False, folder="INBOX"):
    '''puts namedtuple Mailinfo with summary of mailbox contents on q'''
    MInfo = namedtuple('Mailinfo', ['account', 'unread', 'total', 'msgs'])
    try:
        # connect to mailserver
        mail = imaplib.IMAP4_SSL(server)
        mail.login(user, pw)
        mail.list()
        # select inbox
        (allretcode, allmessages_str) = mail.select(folder, readonly=True)
        (unretcode, unmessages) = mail.search(None, '(UNSEEN)')
        if (unretcode, allretcode) == ('OK', 'OK'):
            allmessages_num = int(allmessages_str[0])
            if unmessages[0] == '':
                # no new mails found
                mailinfo = MInfo(account, 0, allmessages_num, [])
            else:
                # new mails found
                unmessages_arr = unmessages[0].split(' ')
                if get_summaries:
                    msgs = get_mails(mail, unmessages_arr)
                else:
                    msgs = []
                mailinfo = MInfo(account, len(unmessages_arr),
                                 allmessages_num, msgs)
        else:
            raise imaplib.IMAP4.error()
    except:
        mailinfo = MInfo(account, None, None)
    finally:
        if mail.state != 'NONAUTH':
            mail.close()
        mail.logout()
    q.put(mailinfo)

    
def get_mails(mail, msg_ids):
    '''return mail summaries for given msg_ids'''
    msgs = []
    EmailSummary = namedtuple('EmailSummary', ['num', 'fromad', 'subject', 'date'])
    try:
        for num in msg_ids:
            typ, data = mail.fetch(num, '(RFC822)')
            msg = email.message_from_string(data[0][1])
            subj = msg['Subject']
            # decode subject if in unicode format
            # TODO: test for UTF-8 better than below
            if 'UTF-8' in subj:
                decd_subj = decode_header(subj)
                # TODO: what is default_charset?
                subj = ''.join([ unicode(t[0], t[1] or default_charset) for t in decd_subj ])
            email_summ = EmailSummary(int(num), msg['From'], subj, None)
            msgs.append(email_summ)
    except:
        # if any errors just don't list mails
        msgs = []
    return msgs

def format_mailsummaries(mailinfos):
    '''takes list of MailInfo tuple & returns formatted string of mails'''
    summstr = ''
    # TODO: build up array & join it instead
    for mailinfo in mailinfos:
        for summ in mailinfo.msgs:
            summstr +=  "[%s] [%0.4d] %.25s  %.40s\n" % (mailinfo.account, summ.num, \
                                                    summ.fromad, summ.subject)
    return summstr

def format_msgcnt(options, accounts):
    '''returns string with account overview (read/unread)'''
    output = ''
    for acct in accounts:
        if options.short:
            output += "%s:%s " % (acct.account[0], acct.unread)
        elif None in (acct.unread, acct.total):
            output += '[%s: unknown] ' % acct.account
        elif options.color and acct.unread > 0:
            output += '[%s: %s%d/%d%s] ' % (acct.account, colmap['HILIT'],
                                acct.unread, acct.total, colmap['NORM'])
        else:
            output += '[%s: %d/%d] ' % (acct.account, acct.unread, acct.total)
    output = output.rstrip()
    return output


def main():
    '''load options, start check threads and display results'''
    cmd_options = getopts()
    config = readconf()
    accounts = config.sections()
    q = Queue.Queue(len(accounts))
    for account in accounts:
        user, pw, server = (config.get(account, 'user'),
                            config.get(account, 'password'),
                            config.get(account, 'server'))
        t = threading.Thread(target=checknew,
                             args = (q, account, user, pw, server,
                                     cmd_options.listmail))
        t.start()
    counts = []
    for account in accounts:
        msg_results = q.get()
        counts.append(msg_results)
    print format_msgcnt(cmd_options, counts)
    # display email summaries if chosen and any new mails
    if cmd_options.listmail and any([msg.unread > 0 for msg in counts]):
        print format_mailsummaries(counts).rstrip()

if __name__ == '__main__':
    main()
