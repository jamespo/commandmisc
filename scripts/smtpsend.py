#!/usr/bin/env python

# smtpsend.py - mailx style tool with SMTP support

import smtplib
from optparse import OptionParser
import sys
from email.mime.text import MIMEText

def send_mail():
    parser = OptionParser()
    parser.add_option("-t", help="to", action="store", dest="to")
    parser.add_option("-f", help="from", action="store", dest="fromad")
    parser.add_option("-s", help="subject", action="store", dest="subject")
    parser.add_option("-x", help="SMTP server", action="store", dest="server",
                      default="localhost")
    (options, args) = parser.parse_args()
    
    msg = MIMEText(sys.stdin.read())
    
    msg['Subject'] = options.subject
    msg['From'] = options.fromad
    msg['To'] = options.to

    s = smtplib.SMTP(options.server)
    s.sendmail(options.fromad, [options.to], msg.as_string())
    s.quit()

if __name__ == '__main__':
    send_mail()
