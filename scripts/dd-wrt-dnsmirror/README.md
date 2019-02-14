dd-wrt-dnsmirror
================

A command line tool to mirror your dd-wrt router dnsmasq DNS to a proper nameserver like BIND (as I couldn't get AXFRs working).

# How it works

* Downloads /tmp/hosts from your router
* Compares it to stored copy if available
* If different create nsupdate file
* Pushes dynamic DNS entries to your nameserver


# Usage

~~~~
usage: dd-wrt-dnsmirror.py [-h] [-e EXE] [-p PRIVKEY] [-s SERVER] [-d DDWRT]
                           [-c CONFIGDIR] [-q]

optional arguments:
  -h, --help            show this help message and exit
  -e EXE, --exe EXE     location of nsupdate
  -p PRIVKEY, --privkey PRIVKEY
                        DNSSEC key
  -s SERVER, --server SERVER
                        DNS server
  -d DDWRT, --ddwrt DDWRT
                        DD-WRT router IP
  -c CONFIGDIR, --configdir CONFIGDIR
                        configdir
  -q, --quiet           quiet mode
~~~~

# Requirements

From stdlib except requires [my fork of openssh-wrapper](https://github.com/jamespo/openssh-wrapper) - see requirements.txt.

# Misc

[Guide to setting zone files & keys](http://agiletesting.blogspot.com/2012/03/dynamic-dns-updates-with-nsupdate-and.html)
