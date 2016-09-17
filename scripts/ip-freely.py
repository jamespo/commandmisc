#!/usr/bin/python3

# ip-freely - update IP address based on results from ipify
# USAGE: ip-freely.py -s ns1.domain.net -n myhome.domain.net -p ~/.priv/domain.net.+157+10183.key

import argparse
import os
import os.path
import sys
import urllib3
import certifi
import re
import tempfile
from subprocess import Popen, PIPE


def getargs():
    '''parse CL args'''
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--exe", default="/usr/bin/nsupdate",
                        help="location of nsupdate")
    parser.add_argument("-p", "--privkey", help="DNSSEC key")
    parser.add_argument("-s", "--server", help="DNS server")
    parser.add_argument("-n", "--hostname", help="hostname to update DNS for")
    parser.add_argument("-r", "--remoteiplookup", default="https://api.ipify.org",
                        help="webservice providing IP lookup")
    return parser.parse_args()

def create_nsupdate_contents(server, domain, hostname, ip, ttl = '1800'):
    '''create file for nsupdate command'''
    content='''server %s.
debug yes
zone %s.
update add %s. %s A %s
show
send''' % (server, domain, hostname, ttl, ip)
    nsfile = tempfile.NamedTemporaryFile(mode='w', delete=False)
    with nsfile:
        nsfile.write(content)
    return nsfile.name

def run_nsupdate(exe, privkey, conffile):
    '''run the nsupdate cmd'''
    cmd = (exe, '-k', privkey, '-v', conffile)
    p = Popen([*cmd], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    if os.getenv("DEBUG") is not None:
        print(stdout, stderr) # DEBUG
    rc = p.returncode
    return (stdout, stderr, rc)
    


def get_remote_ip(remoteiplookup):
    '''lookup external IP'''
    try:
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                                   ca_certs=certifi.where())
        r = http.request("GET", remoteiplookup)  
        ip = r.data.decode("utf-8")
    except:
        # http req failed
        return None
    # ensure output looks like an IP address
    if re.match('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
        return ip
    else:
        return None


def main():
    args = getargs()
    if None in (args.privkey, args.server, args.hostname):
        sys.exit('ERROR: not all args specified')
    if not os.path.isfile(args.privkey):
        sys.exit('ERROR: key files not found')
    ip = get_remote_ip(args.remoteiplookup)
    if ip is None:
        sys.exit('Invalid IP returned')
    # get domain from hostname
    domain = '.'.join(args.hostname.split('.')[1::])
    conffile = create_nsupdate_contents(args.server, domain, args.hostname, ip)
    (stdout, stderr, rc) = run_nsupdate(args.exe, args.privkey, conffile)
    if rc != 0:
        sys.exit("ERROR: nsupdate failed - %s" % stdout + stderr)
    os.remove(conffile)
        
if __name__ == "__main__":
    main()
    
    
