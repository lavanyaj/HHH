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

    dirnameC = '/n/fs/hhh/moof/hhh/results/'+trace+'/5'
    dirname = dirnameC+'/offline'

    allfilenames = [f for f in os.listdir(dirname)]
    allfilenames.sort()
    
    for name in allfilenames:
        
        pickleOfflineFile = open(dirnameC+'/offline/'+name, 'rb')
        offlineHHHReport = pickle.load(pickleOfflineFile)
        pickleOfflineFile.close()


        pickleBasicFile = open(dirnameC+'/basic/'+name+'.pkl', 'rb')
        HHHReport = pickle.load(pickleBasicFile)
        pickleBasicFile.close()

        
        ototal = sum(offlineHHHReport.values())
        total = sum(HHHReport.values())
        if ototal != total:
            print("sums don't match up for " + name)
            print("offline: " + str(round(ototal)))
            print("online: " + str(round(total)))
        
        precision = len(HHHReport)
        recall = len(offlineHHHReport)
        
        for h in offlineHHHReport.keys():
            if h not in HHHReport:
                recall -= 1
        
        for h in HHHReport.keys():
            if h not in offlineHHHReport:
                precision -= 1
        
        print("precision: " + str(round(precision/len(HHHReport), 2)).zfill(4)\
             +"    recall   : " + str(round(recall/len(offlineHHHReport), 2)).zfill(4)\
             +"    name     : " + name)
        
        #e.compareHHH(HHHReport, offlineHHHReport)

if __name__ == '__main__':
        main()




