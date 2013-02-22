#!/usr/bin/perl
# tcpdump -nnlr equinix-sanjose.dirA.20090416-130000.UTC.anon.pcap | ./my*pl "sport"
# tcpdump 3.9.4
# expects line like 08:00:00.000058 ip: 221.45.9.41.80 > 246.193.95.149.2150: . 2898260915:2898262375(1460) ack 1619891163 win 6432

use strict vars;
my $output=$ARGV[0];
my $DEBUG=1;
our ($dip,$sip,$sport,$dport);
my $linenum = 0;
my $second = "0";
my $packetsince = 0;

while (<STDIN>) {
    $linenum = $linenum+1;
    chomp;
#    if (/(\d+:\d+:\d+\.\d+) .+ (\d+\.\d+\.\d+\.\d+)\.(\d+) > (\d+\.\d+\.\d+\.\d+)\.(\d+):/){

#    print "Line: ".$_."\n";
    if (/(\d+:\d+:\d+.)(\d+) [\w\s-!]+ (\d+\.\d+.\d+\.\d+)(\.(\d+))? > (\d+\.\d+.\d+\.\d+)(\.(\d+))?:/) {

#	print "SAW: ", $1, "second is ", $second; #, ",", $2 , ",",  $3, ",", $4;
#	print "are they equal? ", ($1 eq $second), "\n";
#	print "\n";

	$sip = $3;
	$sport = $5;
	$dip = $6;
	$dport = $8;
	
    }
    else {
	print STDERR "ERROR $linenum: $_\n";
	next;
    }


	if ($1 ne $second) {
	    print "Total: ".$packetsince." for ".$second."\n";
	    print "------\n";
	    $packetsince=0;
	}
        
	$second = $1;
    my @fields = split (" ",$_);
    my @tokens = split / /,$output;
    print ${shift(@tokens)};
    for my $token (@tokens) {
	print ','.$$token;
    }
    $packetsince= $packetsince + 1;
    print "\n";
}
	    print "Total: ".$packetsince." for ".$second."\n";
	    print "------\n";
	    $packetsince=0;
	
