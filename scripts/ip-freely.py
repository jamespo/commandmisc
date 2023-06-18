#!/bin/env python3

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
from nslookup import Nslookup
from socket import getaddrinfo


DEBUG = os.getenv('DEBUG')


def getargs():
    '''parse CL args'''
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--exe", default="/usr/bin/nsupdate",
                        help="location of nsupdate")
    parser.add_argument("-p", "--privkey", help="DNSSEC key")
    parser.add_argument("-s", "--server", help="DNS server")
    parser.add_argument("-f", "--force", help="force update even if same",
                        action="store_true")
    parser.add_argument("-t", "--ttl", help="TTL", type=int, default=300)
    parser.add_argument("-n", "--hostname", help="hostname to update DNS for")
    parser.add_argument("-r", "--remoteiplookup", default="https://api.ipify.org",
                        help="webservice providing IP lookup")
    return parser.parse_args()


def create_nsupdate_contents(server, domain, hostname, newip, ttl, currentips):
    '''create file for nsupdate command'''
    # remove existing records if they exist
    del_line = "\n".join([f'update delete {hostname}. A {ip}' for ip in currentips])
    content=f'''server {server}.
debug yes
zone {domain}.
{del_line}
update add {hostname}. {ttl} A {newip}
show
send
quit'''
    nsfile = tempfile.NamedTemporaryFile(mode='w', delete=False)
    with nsfile:
        nsfile.write(content)
    if DEBUG:
        print("---\n%s\n---\n" % content)
    return nsfile.name


def run_nsupdate(exe, privkey, conffile):
    '''run the nsupdate cmd'''
    cmd = (exe, '-k', privkey, '-v', conffile)
    p = Popen([*cmd], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    if DEBUG is not None:
        print("%s\n\n%s\n" % (stdout, stderr))
    rc = p.returncode
    return (stdout, stderr, rc)


def is_ip(ip):
    '''check if ip is an ip'''
    return re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip)


def get_remote_ip(remoteiplookup):
    '''lookup external IP'''
    try:
        timeout = urllib3.Timeout(connect=3.0, read=8.0)
        http = urllib3.PoolManager(
            timeout=timeout,
            cert_reqs='CERT_REQUIRED',
            ca_certs=certifi.where())
        r = http.request("GET", remoteiplookup)
        ip = r.data.decode("utf-8").strip()
        assert is_ip(ip)
        return ip
    except Exception as exc:
        # http req failed
        if DEBUG:
            print('get_remote_ip exception: %s' % exc)
        return None


def get_current_ips(hostname, server):
    '''return current IP(s) for hostname from updating DNS server'''
    try:
        # if dns server is not an ip get the IP
        if not is_ip(server):
            server = getaddrinfo(server, 80)[-1][-1][0]
            if DEBUG:
                print('get_current_ip: dns server ip: %s' % server)
        dns_server = Nslookup(dns_servers=[server], verbose=False, tcp=False)
        dns_query = dns_server.dns_lookup(hostname)
        ips = dns_query.answer
        if DEBUG:
            print('get_current_ip: current record: %s' % ips)
        # ensure returned records look ok
        assert all(is_ip(ip) for ip in ips)
    except:
        ips = []
    finally:
        if DEBUG:
            print('get_current_ip: %s is %s' % (hostname, ips))
        return ips


def main():
    args = getargs()
    if None in (args.privkey, args.server, args.hostname):
        sys.exit('ERROR: not all args specified')
    if not os.path.isfile(args.privkey):
        sys.exit('ERROR: key files not found')
    ip = get_remote_ip(args.remoteiplookup)
    if ip is None:
        sys.exit('Invalid IP returned')
    currentips = get_current_ips(args.hostname, args.server)
    # don't update if record same as new IP
    if (set([ip]) == set(currentips)) and not args.force:
        if DEBUG:
            print('%s is %s - unchanged. No update' % (args.hostname, ip))
        sys.exit()
    # get domain from hostname
    domain = '.'.join(args.hostname.split('.')[1:])
    conffile = create_nsupdate_contents(args.server, domain, args.hostname,
                                        ip, args.ttl, currentips)
    (stdout, stderr, rc) = run_nsupdate(args.exe, args.privkey, conffile)
    os.remove(conffile)
    if rc != 0:
        sys.exit("ERROR: nsupdate failed - %s / %s" % (stdout, stderr))


if __name__ == "__main__":
    main()
    
    
