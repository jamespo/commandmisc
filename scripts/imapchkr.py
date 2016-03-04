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
    config = ConfigParser.ConfigParser()
    config.read(os.path.expanduser('~/.config/.imapchkr.conf'))
    return config


def checknew(q, account, user, pw, server, get_summaries=False, folder="INBOX"):
    '''puts namedtuple Mailinfo with summary of mailbox contents on q'''
    mailinfo = namedtuple('Mailinfo', ['account', 'unread', 'total', 'msgs'])
    mailinfo.msgs = []
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
                (mailinfo.account, mailinfo.unread, mailinfo.total) = \
                (account, 0, allmessages_num)
            else:
                # new mails found
                unmessages_arr = unmessages[0].split(' ')
                (mailinfo.account, mailinfo.unread, mailinfo.total) = \
                    (account, len(unmessages_arr), allmessages_num)
                if get_summaries:
                    mailinfo.msgs = get_mails(mail, unmessages_arr)
        else:
            raise imaplib.IMAP4.error()
    except:
        (mailinfo.account, mailinfo.unread, mailinfo.total) = \
            (account, None, None)
    finally:
        mail.close()
        mail.logout()
    q.put(mailinfo)

    
def get_mails(mail, msg_ids):
    '''return mail summaries for given msg_ids'''
    msgs = []
    try:
        for num in msg_ids:
            typ, data = mail.fetch(num, '(RFC822)')
            msg = email.message_from_string(data[0][1])
            email_summ = namedtuple('EmailSummary', ['num', 'fromad', 'subject', 'date'])
            email_summ.num, email_summ.fromad, email_summ.subject = \
                                                        num, msg['From'], msg['Subject']
        msgs.append(email_summ)
    except:
        # if any errors just don't list mails
        msgs = []
    return msgs

def format_mailsummaries(mailinfos):
    '''takes list of MailInfo tuple & returns formatted string of mails'''
    summstr = ''
    for mailinfo in mailinfos:
        for summ in mailinfo.msgs:
            summstr +=  "[%s] [%4s] %25s %50s\n" % (mailinfo.account, summ.num, \
                                                    summ.fromad, summ.subject)
    return summstr

def format_msgcnt(options, accounts):
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
