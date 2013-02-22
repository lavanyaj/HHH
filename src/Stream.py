#!/usr/bin/env python
# encoding: ASCII
import logging
import sys
import os
import pickle
from collections import Counter
logging.basicConfig()#level=logging.DEBUG)

class Stream: 
   
    def __init__(self, dirname, files_at_a_time, max_intervals):
        self.dirname = dirname
        self.streamtotal = 0
        self.max = 0
        self.max_intervals = max_intervals
        self.files_at_a_time = files_at_a_time
        allfiles = [f for f in os.listdir(dirname)]
        allfiles.sort()
        while (len(allfiles) < files_at_a_time * max_intervals):
            allfiles.extend(allfiles)
            
        self.files = allfiles[:files_at_a_time*max_intervals+1]
        self.intervalCounters = {}

    def getMax(self):
        if self.max > 0:
            return self.max
        
        temp = 0
        for index in range(0, self.max_intervals):
            intervalCounter = Counter()
            for filenum in range(0, self.files_at_a_time):
                fileindex = index * self.files_at_a_time + filenum
                filehandle = open(self.dirname+'/'+self.files[fileindex], 'rb')
                intervalCounter.update(pickle.load(filehandle))
            total = sum(intervalCounter.values())
            self.streamtotal += total
            if total > temp:
                temp = total
        
        self.max = temp
        return self.max
    
    def getCounterNames(self):
        l = list(self.intervalCounters.keys())
        l.sort()
        return l

    def updateCounters(self):
        for index in range(0, self.max_intervals):
            # name of last pickle file in this interval
            # so this counter contains packets upto [, intervalname)
            intervalname = self.files[(index+1)*self.files_at_a_time]
            self.intervalCounters[intervalname] = Counter()
            for filenum in range(0, self.files_at_a_time):
                fileindex = index * self.files_at_a_time + filenum
                filehandle = open(self.dirname+'/'+self.files[fileindex], 'rb')
                self.intervalCounters[intervalname].update(pickle.load(filehandle))
