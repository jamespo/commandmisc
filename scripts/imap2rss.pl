#!/usr/bin/perl

# imap2rss.pl - generate RSS feed from IMAP inbox
# uses code from Net::IMAP::Simple docs
# v0.1 by James Powell - Jun 2009 - licensed under GPL v3

# USAGE: run this in cron and redirect to a page under your web root
# */5 * * * *  /usr/local/bin/imap2rss.pl > /web/mymail.rdf
# you should protect the page, or at least make it difficult to guess
# the URL

# conf file lives in ~/.priv/.imap2rss
# FORMAT user:pass:server

use Net::IMAP::Simple;
use Email::Simple;
use XML::RSS;
use Data::Dumper; # DEBUG
use strict;

# load conf file 

my $conf = $ENV{HOME} . '/.priv/.imap2rss';
die "$conf does not exist" unless (-f $conf);

open(CONF, $conf);
my $cl = <CONF>;
chomp($cl);
my ($user, $pass, $server) = split /:/, $cl;
close(CONF);

my @mails;

# Create the object
my $imap = Net::IMAP::Simple->new($server) ||
    die "Unable to connect to IMAP: $Net::IMAP::Simple::errstr\n";

# Log on
if(!$imap->login($user, $pass)){
    print STDERR "Login failed: " . $imap->errstr . "\n";
    exit(64);
}

# select the INBOX
my $nm = $imap->select('INBOX');

# put from, subject, date into @mails
for(my $i = 1; $i <= $nm; $i++){
    my $es = Email::Simple->new(join '', @{ $imap->top($i) } );

    unshift @mails, [$imap->seen($i) ? '*' : ' ', $i, $es->header('From'), 
		  $es->header('Subject'), $es->header('Date')];
}

$imap->quit;

print Dumper(\@mails) if ($ENV{DEBUG});



# Display the RSS

# for date calcs
my @mons = qw{FILLER Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec};
my $idx = 0;
my %mon2num = map { $_ => $idx++ } @mons;

my $rss = new XML::RSS (version => '1.0');

my $title_txt = "$user INBOX";
my $desc = $title_txt . " @ $server";
my $link = 'about:blank';

$rss->channel(
              title        => $title_txt,
              link         => $link,
              description  => $desc
	      );

foreach (@mails) {

    $rss->add_item(title => $_->[2] . ' - ' . $_->[3],
                   link  => $link,
                   dc => { date =>   &conv_date($_->[4]) }
                   );

}

print $rss->as_string;


sub conv_date {
    my $date = shift;

    # example = Mon, 30 Mar 2009 12:44:57 +0100
    # output 2000-01-01T12:00+00:00

    my ($day, $month, $year, $time, $offset) = $date =~ /^\w\w\w, (\d\d?) (\w\w\w) (\d\d\d\d) (\d\d:\d\d):\d\d (\+\d\d\d\d)?$/;

    # clean up offset
    if ($offset eq '') { $offset = '0000'; }
    $offset =~ s/^(\d\d)(\d\d)$/$1:$2/;

    my $outstr = sprintf "%s-%02d-%02dT%s+%s", $year, $mon2num{$month}, $day, $time, $offset;

    if ($ENV{DEBUG}) { print "$date - $month - OUT: $outstr\n"; }

    return $outstr;
}

