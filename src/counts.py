#!/usr/bin/env python
# encoding: ASCII
"""
counts.py
Created by Lavanya Jose on 2011-05-29.
Copyright (c) 2011 . All rights reserved.

###Created by Lavanya  Jose on 2010-10-19.
###Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import pickle
import fileinput
from collections import Counter 

def main():
    # group by 1 or 5 or 60 seconds
    # I think unix timestamp would be easier to group by whatever

    by_seconds = True
    pklsDirectory='/n/fs/hhh/moof/hhh/pkls/'
    trace='equinix-sanjose.dirB.20090917'
    gran = 5
    cnt = {}
    toofewwords = Counter()
    toofewsrctuples = Counter()
    nixtime = 0
    notimeonline = 0
    for line in fileinput.input(sys.argv[1]):
        words = line.rstrip("\n").split()
        # words[0] -- 13:31:37.258527
        times = words[0].split(":")
        if len(times) < 3:
            notimeonline += 1
        hour = int(times[0])
        minute = int(times[1])
        seconds = times[2].split(".")
        second = int(seconds[0])
		# seconds since start of day
        dsec = hour * 3600 + minute * 60 + second
		# day_seconds = 48697
                
	    # rounding
        rsec = str(dsec + (gran - dsec%gran)).zfill(5)
									
        if len(words) < 5:
            toofewwords[rsec] += 1
            continue

        srcip = words[2].split(".")
		# sometimes don't get complete IP

        if (len(srcip) < 4):
            toofewsrctuples[rsec] += 1
            continue
        # sometimes get more than 4 
        fullip = '.'.join([str(srcip[num]) for num in range(0,4)])
                
		# make a new counter for pkts
		# seen in [rsec - gran, rsec)

        if rsec not in cnt:
            cnt[rsec] = Counter()
            print (rsec)
                
        # num pkts from fullip in [rsec - gran, rsec)
        cnt[rsec][fullip] += 1

        
    for rsec in cnt:
        output = open(pklsDirectory+str(trace)+'/'+str(gran)+'/' + rsec +'.pkl', 'wb')
        # dump {<srcip, count>, srcip seen in [rsec - gran, rsec)}
        # in output file
        pickle.dump(cnt[rsec], output)
        pickle.dump(toofewwords[rsec], output)
        pickle.dump(toofewsrctuples[rsec], output)
        pickle.dump([sys.argv[1], gran, notimeonline], output)
        print (rsec)
        output.close()

if __name__ == '__main__':
        main()
