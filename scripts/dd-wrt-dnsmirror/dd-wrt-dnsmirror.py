#!/usr/bin/env python3

# dd-wrt-dnsmirror.py - mirror dd-wrt dnsmasq dns

from openssh_wrapper import SSHConnection  # https://github.com/jamespo/openssh-wrapper
from subprocess import Popen, PIPE
import argparse
import hashlib
import os.path
import os
import re
# import sys
import tempfile


class DDWRT_Remotefile():
    '''retrieve dd-wrt hosts file'''
    def __init__(self, ip, dnsdir, user='root'):
        self._mkdir(dnsdir)
        self.dnsdir = dnsdir
        self.user = user
        self.ip = ip
        self.retrieve_hosts()

    @staticmethod
    def _mkdir(dir):
        '''create dir if required'''
        if os.path.isdir(dir):
            return
        os.mkdir(dir)

    def retrieve_hosts(self, remfile='/etc/hosts'):
        '''get dd-wrt hosts file'''
        conn = SSHConnection(self.ip, login=self.user)  # ssh key must exist on dest
        conn.scpget(remfile, self.dnsdir)
        self.filename = os.path.join(self.dnsdir, os.path.basename(remfile))


class DDWRT_DNS():
    ''' parse & manipulate dd-wrt hosts file'''
    def __init__(self, filename):
        self.filename = filename
        self.load()

    def load(self):
        '''load hosts file into self.contents & generate hash'''
        try:
            with open(self.filename) as f:
                self.contents = f.read()
            self.hash = hashlib.sha1(self.contents.encode('utf-8')).hexdigest()
        except FileNotFoundError:
            self.contents = ''
            self.hash = None

    def __eq__(self, other):
        '''compare 2 DDWRT_DNS objects'''
        # TODO: compare sorted parsed host lists in case of order change?
        return self.hash == other.hash

    def orig_filename(self):
        '''return master filename'''
        return self.filename + ".ORIG"

    def unlink(self):
        '''remove hosts file'''
        os.remove(self.filename)

    def make_orig(self, target_filename=None):
        '''make this file the master'''
        if target_filename is None:
            target_filename = self.orig_filename()
        os.rename(self.filename, target_filename)
        self.filename = target_filename

    def parse(self):
        '''parse self.filename into self.hosts dict & set self.domain'''
        self.hosts = {}   # host to IP dict
        self.domain = None
        lines = self.contents.splitlines()
        hostline_re = re.compile(r"(\d+\.\d+\.\d+\.\d+)\s+([^.]+)\.([^.]+)")
        # go through file, populate self.hosts
        for line in lines:
            match = re.match(hostline_re, line)
            if match:
                self.hosts[match.group(2)] = match.group(1)
                if self.domain is None:
                    self.domain = match.group(3)


class DD_UpdateDNS():
    '''update DNS'''
    def __init__(self, ddwrt_dns, cli_args):
        self.dd = ddwrt_dns
        self.args = cli_args

    def create_nsupdate_contents(self, ttl='1800'):
        '''create file for nsupdate command'''
        content = "server %s.\ndebug yes\nzone %s.\n" % (self.args.server,
                                                         self.dd.domain)
        # loop round hosts
        for host, ip in self.dd.hosts.items():
            content += "update add %s.%s %s IN A %s\n" % (host, self.dd.domain, ttl, ip)
        content += "show\nsend\n"
        nsfile = tempfile.NamedTemporaryFile(mode='w', delete=False)
        with nsfile:
            nsfile.write(content)
        if os.getenv("DEBUG"):
            print("temp nsupdate file: %s" % nsfile.name)
        self.nsfilename = nsfile.name

    def run_nsupdate(self):
        '''run the nsupdate cmd'''
        cmd = (self.args.exe, '-k', self.args.privkey, '-v', self.nsfilename)
        p = Popen([*cmd], stdout=PIPE, stderr=PIPE)
        (stdout, stderr) = p.communicate()
        if os.getenv("DEBUG") is not None:
            print(stdout, stderr)  # DEBUG
        rc = p.returncode
        os.remove(self.nsfilename)  # Remove temporary nsupdate file
        return (stdout, stderr, rc)


def validate_args():
    '''get user, pass, config dir'''
    parser = argparse.ArgumentParser()
    dnsdir_default = os.path.join(os.path.expanduser("~"), '.config',
                                  'ddwrtdns')
    parser.add_argument("-e", "--exe", default="/usr/bin/nsupdate",
                        help="location of nsupdate")
    parser.add_argument("-p", "--privkey", help="DNSSEC key")
    parser.add_argument("-s", "--server", help="DNS server", default="localhost")
    parser.add_argument("-d", "--ddwrt", help="DD-WRT router IP")
    parser.add_argument("-c", "--configdir", help="configdir",
                        default=dnsdir_default)
    parser.add_argument("-q", "--quiet", help="quiet mode",
                        action='store_true', default=False)
    args = parser.parse_args()
    # TODO: check args for None & throw exception if necessary
    return args


def hosts_changed(dd, dd_orig):
    '''if hosts file changed from master parse & replace master'''
    dd.parse()
    if dd != dd_orig:
        # hosts file changed
        dd.make_orig()  # rename to "master"
        return True
    else:
        dd.unlink()
        return False


def main():
    args = validate_args()
    ddrf = DDWRT_Remotefile(args.ddwrt, args.configdir)
    dd = DDWRT_DNS(ddrf.filename)
    dd_orig = DDWRT_DNS(dd.orig_filename())
    if hosts_changed(dd, dd_orig):
        # for now just push all records
        if os.getenv("DEBUG"):
            print('hosts changed')
        dd_update = DD_UpdateDNS(dd, args)
        dd_update.create_nsupdate_contents()
        dd_update.run_nsupdate()
        msg = "%s updated" % dd.domain
    else:
        msg = "No change - %s not updated" % dd.domain
    if not args.quiet:
        print(msg)


if __name__ == '__main__':
    main()
