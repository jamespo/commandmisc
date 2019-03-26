#!/usr/bin/env python3

# imapchkr.py - checks for new messages in IMAP server
# (c) James Powell - jamespo [at] gmail [dot] com 2014
# Create ~/.config/.imapchkr.conf with 1 or more sections as below:
# [serveralias]
# user=james
# password=2347923rbkaa
# server=yourimapserver.com

from email.header import make_header, decode_header
import os
import imaplib
import email
from email.utils import parseaddr
from optparse import OptionParser
from collections import namedtuple
import configparser
import queue
import threading

# tuple of shell colour codes
colmap = namedtuple('ColMap', ['norm', 'white', 'blue', 'yellow', 'green'])
colm = colmap('\033[0m', '\033[37;1m', '\033[36;1m', '\033[33;1m', '\033[32;1m')


def getopts():
    '''returns OptionParser.options for CL switches'''
    parser = OptionParser()
    parser.add_option("-b", help="b/w output", action="store_false",
                      dest="color", default=True)
    parser.add_option("-s", help="short output", action="store_true",
                      dest="short", default=False)
    parser.add_option("-l", help="list mail summary", action="store_true",
                      dest="listmail", default=False)
    (options, args) = parser.parse_args()
    return options


def readconf():
    '''returns ConfigParser object with account details'''
    config = configparser.ConfigParser()
    config.read(os.path.expanduser('~/.config/.imapchkr.conf'))
    return config


def checknew(q, account, user, pw, server, get_summaries=False, folder="INBOX"):
    '''puts namedtuple Mailinfo with summary of mailbox contents on q'''
    MInfo = namedtuple('Mailinfo', ['account', 'unread', 'total', 'msgs'])
    try:
        # connect to mailserver
        mail = imaplib.IMAP4_SSL(server)
        if server == 'imap.gmail.com':
            # doesn't support cram_md5
            loginstatus, logincomment = mail.login(user, pw)
        else:
            loginstatus, logincomment = mail.login_cram_md5(user, pw)
        assert loginstatus == 'OK'
        mail.list()
        # select inbox
        mailinfo = count_mails(mail, MInfo, folder, account, get_summaries)
    except:
        mailinfo = MInfo(account, None, None, None)
    finally:
        if mail.state != 'NONAUTH':
            mail.close()
        mail.logout()
    q.put(mailinfo)


def count_mails(mail, MInfo, folder, account, get_summaries):
    '''count the mails & return MailInfo tuple'''
    (allretcode, allmessages_str) = mail.select(folder, readonly=True)
    (unretcode, unmessages) = mail.search(None, '(UNSEEN)')
    if (unretcode, allretcode) == ('OK', 'OK'):
        allmessages_num = int(allmessages_str[0])
        unread = unmessages[0].decode("utf-8")
        if unread == '':
            # no new mails found
            mailinfo = MInfo(account, 0, allmessages_num, [])
        else:
            # new mails found
            unmessages_arr = unread.split(' ')
            if get_summaries:
                msgs = get_mails(mail, unmessages_arr)
            else:
                msgs = []
            mailinfo = MInfo(account, len(unmessages_arr),
                             allmessages_num, msgs)
    else:
        raise imaplib.IMAP4.error()
    return mailinfo


def get_mails(mail, msg_ids):
    '''return mail summaries for given msg_ids'''
    msgs = []
    EmailSummary = namedtuple('EmailSummary', ['num', 'fromad', 'subject', 'date'])
    try:
        for num in msg_ids:
            typ, data = mail.fetch(num, '(RFC822)')
            msg = data[0][1]
            msg = msg.decode('utf-8')
            msg = email.message_from_string(msg)
            email_summ = EmailSummary(int(num), clean_address(msg['From']),
                                      clean_subject(msg['Subject']), None)
            msgs.append(email_summ)
    except Exception as ex:
        # if any errors just don't list mails
        print("error: %s" % ex)
        msgs = []
    return msgs


def clean_address(email_addr):
    '''return clean from address'''
    clean_addr = parseaddr(email_addr)
    return unicode_to_str(clean_addr[0] or clean_addr[1])


def clean_subject(subj):
    '''decode subject if in unicode format'''
    subj = unicode_to_str(subj)
    # remove newlines
    subj = subj.replace('\r', '')
    subj = subj.replace('\n', '')
    return subj


def unicode_to_str(header):
    '''convert unicode header to plain str if required'''
    return str(make_header(decode_header(header)))


def format_mailsummaries(options, mailinfos, acct_cols):
    '''takes list of MailInfo tuple & returns formatted string of mails'''
    ac_max_len = max((len(mailinfo.account) for mailinfo in mailinfos))
    summaries = []
    for mailinfo in mailinfos:
        account_name = mailinfo.account
        if options.color:
            account_name = '%s%s%s' % (acct_cols[account_name],
                                       account_name, colm.norm)
        # spaces to pad account name with (colouring breaks padding)
        acct_spc = ' ' * (ac_max_len - len(mailinfo.account))
        s_fmt = '[{acct_spc}{acct}] [{summ.num:04d}] {summ.fromad:25} {summ.subject:40}'
        for summ in mailinfo.msgs:
            summaries.append(s_fmt.format(acct=account_name,
                                          ac_max_len=ac_max_len,
                                          summ=summ, acct_spc=acct_spc))
    return "\n".join(summaries)


def format_msgcnt(options, mailtotals, acct_cols):
    '''returns string with account overview (read/unread)'''
    output = ''
    for mailtotal in mailtotals:
        account_name = mailtotal.account
        if options.color:
            account_name = '%s%s%s' % (acct_cols[account_name], account_name,
                                       colm.norm)
        if options.short:
            output += "%s:%s " % (account_name[0], mailtotal.unread)
        elif None in (mailtotal.unread, mailtotal.total):
            output += '[%s: unknown] ' % account_name
        elif options.color and mailtotal.unread > 0:
            output += '[%s: %s%d/%d%s] ' % (account_name, colm.white,
                                            mailtotal.unread, mailtotal.total, colm.norm)
        else:
            output += '[%s: %d/%d] ' % (account_name, mailtotal.unread, mailtotal.total)
    output = output.rstrip()
    return output


def main():
    '''load options, start check threads and display results'''
    cmd_options = getopts()
    config = readconf()
    accounts = config.sections()
    q = queue.Queue(len(accounts))
    for account in accounts:
        user, pw, server = (config.get(account, 'user'),
                            config.get(account, 'password'),
                            config.get(account, 'server'))
        t = threading.Thread(target=checknew,
                             args = (q, account, user, pw, server,
                                     cmd_options.listmail))
        t.start()
    mailtotals = []
    acct_cols = {}  # dict of account name : colour
    for acct_num, account in enumerate(accounts):
        msg_results = q.get()
        mailtotals.append(msg_results)
        # store colour for account
        acct_cols[account] = colm[ (acct_num % (len(colm)-2))+2 ]
    print(format_msgcnt(cmd_options, mailtotals, acct_cols))
    # display email summaries if chosen and any new mails
    if cmd_options.listmail and any((msg.unread > 0 for msg in mailtotals)):
        print(format_mailsummaries(cmd_options, mailtotals, acct_cols))

if __name__ == '__main__':
    main()
