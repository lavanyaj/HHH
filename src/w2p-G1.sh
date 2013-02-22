#!/bin/csh
#
#***
#*** "#PBS" lines must come before any non-blank, non-comment lines ***
#***
#
# 1 node, 1 CPU per node (total 1 CPU), wall clock time of 30 hours
#
#PBS -l walltime=10:00:00,nodes=1:ppn=1
#
# merge STDERR into STDOUT file
#PBS -j oe
#
# send mail if the process aborts, when it begins, and
# when it ends (abe)


#

# 060000 pcap contains [130000, 130001) GMT
# its 1 second pickle in seconds(130001).pkl

if ($?PBS_JOBID) then
	echo "Starting" $PBS_JOBID "at" `date` "on" `hostname`
	echo ""
else
	echo "This script must be run as a PBS job"
	exit 1
endif

cd $PBS_O_WORKDIR

#equinix-sanjose.dirB.20090917-130500.UTC.anon.pcap
#set urlday='https://data.caida.org/datasets/passive-2009/equinix-sanjose/20090416-130000.UTC'
set hhmmss='131400'
set raw='raw'
set trace='equinix-sanjose.dirB.20090917'
set dir='/n/fs/hhh/HHH'
#set python='/n/fs/ugrad/ug12/ljose/Python-3.1.2/python' 
set suff='UTC.anon'
set G=1


echo "$hhmmss"

set rawfiledir=$dir/$raw
set tracefilename=$trace-$hhmmss.$suff
set tracefiledir='/n/fs/hhh/lavanya/pcap'
set tracefile=$tracefilename
set pcapfile=$tracefile.pcap
set gzfile=$pcapfile.gz
set codedir='/n/fs/ugrad/ug12/ljose/git/HHH/src'

echo "tcpdumping $tracefiledir/$pcapfile"

#(tcpdump -nnlr $tracefiledir/$pcapfile | $codedir/mytcpdump2csv.pl "dport" | python $codedir/distinctT.py $T > python secondsketcher.py $rawfiledir/dp-$hhmmss-$hhmmss.T$T.raw) >& $rawfiledir/dp-$hhmmss-$hhmmss.T$T.err

(tcpdump -nnlr $tracefiledir/$pcapfile | $codedir/mytcpdump2csv.pl "sip" > $rawfiledir/sip-$hhmmss.raw) >& $rawfiledir/sip-$hhmmss.err

time csplit -k -f $rawfiledir/sip-$hhmmss.raw_ $rawfiledir/sip-$hhmmss.raw '/---/1' "{12}"
#time split -l 4000000 $rawfiledir/dp-$hhmmss-$hhmmss.T$T.raw $rawfiledir/dp-$hhmmss-$hhmmss.T$T.raw_

#awk '/Total/{n++}{print > rawfiledir/sip-$hhmmss.raw"_"n}' rawfiledir/sip-$hhmmss.raw 

echo ""
echo "Done at " `date`
