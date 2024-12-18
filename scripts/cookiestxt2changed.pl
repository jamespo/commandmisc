#!/usr/bin/perl

# cookiestxt2changed.pl - convert cookies.txt file to format suitable for use in changedetection.io
# USAGE: cookiestxt2changed.pl cookies.txt

my @cookies;

while (<>) {
    chomp;
    my @cookie = split /\t/;
    if ($#cookie < 6) { next; }
    #print @cookies;
    push(@cookies, $cookie[5] . '=' . $cookie[6]);
}

print "Cookie: " . join('; ', @cookies);
