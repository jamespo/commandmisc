#!/usr/bin/env python

# clamsmtp-action.py - VirusAction script for clamsmtp
# based on smtpsend.py

import smtplib
from optparse import OptionParser
import sys
import os
from email.mime.text import MIMEText

def send_mail():
    parser = OptionParser()
    parser.add_option("-t", help="to", action="store", dest="to")
    parser.add_option("-f", help="from", action="store", dest="fromad",
                      default="clamsmtp")
    parser.add_option("-s", help="subject", action="store", dest="subject",
                      default = "VIRUS found")
    parser.add_option("-x", help="SMTP server", action="store", dest="server",
                      default="localhost")
    (options, args) = parser.parse_args()
    
    body = ("An email virus has been blocked", "",
            "The supposed sender was: %s" % os.environ.get('SENDER'), "",
            "The recipient(s) were: %s" % os.environ.get('RECIPIENTS'), "",
            "Virus name is: %s" % os.environ.get('VIRUS'), "",
            "Remote Client IP is: %s" % os.environ.get('CLIENT', 'UNKNOWN'), "",
            "Quarantine file saved in: %s" % os.environ.get('EMAIL', 'NOT SAVED'), "")
    body_str = "\n".join(body)

    msg = MIMEText(body_str)
    
    msg['Subject'] = options.subject
    msg['From'] = options.fromad
    msg['To'] = options.to
    
    s = smtplib.SMTP(options.server)
    s.sendmail(options.fromad, [options.to], msg.as_string())
    s.quit()

if __name__ == '__main__':
    send_mail()
