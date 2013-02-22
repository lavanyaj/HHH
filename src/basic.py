#!/usr/bin/env python
# encoding: ASCII

import sys
import os
import pickle
from collections import Counter
import HHH
import TCAM
import Stream


def main():
    """command-line arguments
    from pkls/trace/? (5 or 1)
    measuring interval? 
        (if M = 10s and you put 5 above, write 2 at_a_time)
    """
    at_a_time = 1
    gran = 5
    trace = 'equinix-sanjose.dirB.20090917'
    max_intervals = 150
    seconds = gran * at_a_time 
    dirnameP = '/n/fs/hhh/moof/hhh/pkls/'+trace+'/5'
    dirnameC = '/n/fs/hhh/moof/hhh/results/'+trace+'/5'
    s = Stream.Stream(dirnameP, at_a_time, max_intervals)
    s.getMax()
    s.updateCounters()
    
    h = HHH.HHH(int(s.max/10), 32)
    t = TCAM.TCAM()
    
    result = h.start()
    nextTCAMList = result[0]
    monitoredHHHes = result[1]

    intervalnames = s.getCounterNames()
    
    for name in intervalnames:
        counts = s.intervalCounters[name]
        offline_result = h.offline(counts)
        offlineHHHReport = offline_result[2]

        pickleOfflineFile = open(dirnameC+'/offline/'+name, 'wb')
        pickle.dump(offlineHHHReport, pickleOfflineFile)
        pickleOfflineFile.close()

        TCAMCounts = t.philter(counts, nextTCAMList)
        result = h.run(TCAMCounts, monitoredHHHes)
        
        nextTCAMList = result[0]
        monitoredHHHes = result[1]
        HHHReport = result[2]
        
        pickleBasicFile = open(dirnameC+'/basic/'+name+'.pkl', 'wb')
        pickle.dump(HHHReport, pickleBasicFile)
        pickleBasicFile.close()

        
        stats = "dirnameP " + str(dirnameP) + "; at_a_time " + str(at_a_time)\
        + "; max_intervals " + str(max_intervals) + "; so seconds " + str(seconds)\
        + "; HHHReport dumped in " + dirnameC+'/basic/'+name+'.pkl'\
        + "; offlineHHHReport dumped in " + dirnameC+'/offline/'+name+'.pkl'\
        + "; s.files " + str(s.files)
        
        List = [str(dirnameP), at_a_time, max_intervals, seconds, \
        dirnameC+'/basic/'+name+'.pkl', dirnameC+'/offline/'+name+'.pkl',\
        str(s.files)]
        
        pickleStatsFile = open(dirnameC+'/stats/'+name+'.pklstats', 'wb')
        pickle.dump(stats, pickleStatsFile)
        pickle.dump(List, pickleStatsFile)
        pickleStatsFile.close()
        #e.compareHHH(HHHReport, offlineHHHReport)

if __name__ == '__main__':
        main()




