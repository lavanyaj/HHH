#!/usr/bin/env python
# encoding: ASCII
import logging
import sys
import os
import TCAM
import pickle
#from collections import Counter
import copy


logging.basicConfig()#level=logging.DEBUG)

class HHH: 
    """ simulates HHH algorithm module for one run
        
        output: list of TCAM rules to monitor (stored in nextTCAMList)
        input: Dict of counts for those TCAM rules (process(Dict))
        can access: HHH() to initialize, process(), nextTCAMList, 
        nextMonitorHHHes, HHHReport after each process,
        
        Btw you only need to do
        import HHH
        
        h = HHH.HHH() #initialize
        
        result = h.start()
        nextTCAMList = result[0] # this is a list
        monitoredHHHes = result[1] # also a list

        repeat:
            #get TCAMCounts using nextTCAMList
            
            # TCAMCounts is a Counter() with all the 
            # prefixes in TCAMList, set them to 0
            # explicitly if that prefix didn't match
            # any packets
            
            # You can make a Counter from a dict
            # with just c = Counter(dict)
            
            result = h.run(TCAMCounts, monitoredHHHes)
        
            nextTCAMList = result[0]
            monitoredHHHes = result[1]
            HHHReport = result[2] # this is a dict
    """
    
    def __init__(self, H, leafBits):
        """initialize list of HHHes to monitor and TCAM rule-list
        
            Keyword arguments:
            H -- threshold 
            ex. 10 if for this run, looking at HHHes w > 10 pkts
            every interval
            leafBits -- how many bits does a leaf have
            ex. if '.0010' is a leaf, leafBits is 4

        """
        self.H = H
        self.leafBits = leafBits

        return

    def start(self):
        nextMonitorHHHes = ['.']
        nextTCAMList = self.makeTCAMList(nextMonitorHHHes)
        
        return [nextTCAMList, nextMonitorHHHes]

    
    def offline(self, counts):
        result = self.start()
        nextTCAMList = result[0]
        monitoredHHHes = result[1]
        logging.debug("offline ... ")
        logging.debug("counts " + str(counts))
        logging.debug("result " + str(result))
        
        oldTCAMList = []
        t = TCAM.TCAM()
        while oldTCAMList != nextTCAMList:
            oldTCAMList = list(nextTCAMList)
            TCAMCounts = t.philter(counts, nextTCAMList)
            logging.debug("TCAMCounts " + str(TCAMCounts))
            logging.debug("monitoredHHHes " + str(monitoredHHHes))
            result = self.run(TCAMCounts, monitoredHHHes)
            logging.debug("result " + str(result))

            nextTCAMList = result[0]
            monitoredHHHes = result[1]
        logging.debug("offline OVER----------------------- ")
        return result
    
    def ancOf(self, prefix, Set):
        # ex. for prefix ='.123456' anc = ['.1234567', '.123456', ... , '.']
        anc = [prefix] + list(map(lambda l: prefix[:-l], range(1, len(prefix)))) 
        logging.debug("in ancOf " + prefix)
        logging.debug("set" + str(Set))
        logging.debug("anc " + str(anc))  
        for a in anc:
                if a in Set:
                        logging.debug("anc returned a")
                        return a        
    
    def run(self, TCAMDict, monitoredHHHes):
        """analyze TCAM counts to get HHH report and next rule-set
        
        Keyword arguments:
        TCAMDict -- <prefix, count> where prefixes from nextTCAMList
        ex. if nextTCAMList was ['.0001', '.0', '.1']
            TCAMdict could be {'.0001':10, '.0':5, '.1':15}
        
        Result:
        HHHReport -- HHHes and their TCAM counts
        nextMonitorHHHes -- next list of HHHes to monitor
        nextTCAMList --  TCAM rules for nextMonitorHHHes (kids) 
        
        """
        logging.debug("run")
        # check nextTCAMList and TCAMDict keys are same
        packets_counted = sum(TCAMDict.values())
        MyTCAMDict = copy.deepcopy(TCAMDict) # copy
        TCAMSet = set(TCAMDict.keys())
        myMonitoredHHHes = sorted(monitoredHHHes, reverse=True, key=len) # reverse sorted
        logging.debug(myMonitoredHHHes)
        nextMonitorHHHes = []

        # for each monitored HHH: three cases- root, leaf or neither
        # MyTCAMDict -- we'll "remove" rules and adjust counts accordingly
        # so finally have just enough to report HHHes

        for prefix in myMonitoredHHHes:
            logging.debug("looking at HHH " + str(prefix))    
            leftChild = prefix+'0'
            rightChild = prefix+'1'

            if self.isRoot(prefix):
                logging.debug(prefix + "is a root")
                prefixCount = MyTCAMDict[leftChild] + MyTCAMDict[rightChild]
                nextMonitorHHHes.append(prefix)
            # whatever, always need rules for .0 and .1
                if MyTCAMDict[leftChild] > self.H:
                    nextMonitorHHHes.append(leftChild)
                if MyTCAMDict[rightChild] > self.H:
                    nextMonitorHHHes.append(rightChild)
                                
        
            elif self.isLeaf(prefix):
                prefixCount = MyTCAMDict[prefix]
                logging.debug(prefix + "is a leaf, it's count is " + str(MyTCAMDict[prefix]))
                if prefixCount < self.H:
            # won't report prefix as an HHH, so okay if we didn't have
            # rule for prefix (it was a leaf HHH, so rules for it, not children)
                    MyTCAMDict[self.ancOf(self.getParent(prefix), TCAMSet)] += prefixCount
                    logging.debug("rolling over " + str(prefixCount) + " to " + self.ancOf(self.getParent(prefix), TCAMSet))
                    MyTCAMDict[prefix] = 0
                else:
                    nextMonitorHHHes.append(prefix)
                
            else:
                prefixCount = MyTCAMDict[leftChild] + MyTCAMDict[rightChild]
                logging.debug(prefix + ":\nleftChild -- " + str(MyTCAMDict[leftChild]))
                logging.debug("rightChild -- " + str(MyTCAMDict[rightChild]))
                logging.debug("prefixCount -- " + str(prefixCount))
                
                if prefixCount < self.H:
                # won't report prefix as an HHH, so okay if we didn't have
                # rules for children
                    MyTCAMDict[self.ancOf(prefix, TCAMSet)] += prefixCount
                    logging.debug("rolling over " + str(prefixCount) + " to " + self.ancOf(prefix, TCAMSet))
                    MyTCAMDict[leftChild] = 0
                    MyTCAMDict[rightChild] = 0
                
                elif MyTCAMDict[leftChild] > self.H or MyTCAMDict[rightChild] > self.H:
            # won't report prefix as HHH then, so okay if we didn't have
            # rule for a below threshold child
                    for child in [leftChild, rightChild]:
                        if MyTCAMDict[child] > self.H:
                            nextMonitorHHHes.append(child)
                        else:
                            MyTCAMDict[self.ancOf(prefix, TCAMSet)] += MyTCAMDict[child]
                            logging.debug("rolling over non HHH child (" + str(child) + ")'s" + str(MyTCAMDict[child]))# + " to " + self.ancOf(prefix, TCAMSet))
                            MyTCAMDict[child] = 0
                else:
            # will report prefix as an HHH, needed rules for both children
            # to confirm
                    nextMonitorHHHes.append(prefix)
        
        ## DESTROYING OLD TCAM LIST, MAKING NEW ONE##
        nextTCAMList = self.makeTCAMList(nextMonitorHHHes)
        HHHReport = self.report(MyTCAMDict, nextMonitorHHHes)
        packets_reported = sum(HHHReport.values())
        
        if (packets_counted != packets_reported):
            print("don't trust me, i'm against conserving packets")
            print("packets counted: " + str(packets_counted))
            print("packets reported: " + str(packets_reported))
            print("MyTCAMDict: " + str(MyTCAMDict))
        logging.debug("run OVER-----------------------")
        return [nextTCAMList, nextMonitorHHHes, HHHReport]
            
    def makeTCAMList(self,monitoredHHHes):
        """make TCAM rule-list need to monitor monitoredHHHes
        
            Keyword arguments:
            monitoredHHHes
            
            TCAM rule-list is just monitor both kids for each
            HHH, unless it's a leaf, in which case you just monitor
            the leaf.

        """
        TCAMList = []
        for prefix in monitoredHHHes:
            if self.isLeaf(prefix):
                TCAMList.append(prefix)
            else:
                TCAMList.append(prefix+'0')
                TCAMList.append(prefix+'1')
        TCAMList.sort(reverse=True, key=len)
        return TCAMList  
    
    def showHHHes(self, HHHReport):
        """show report
        
            Keyword arguments:
            report -- from self.report after a process

        """
        for hhh in HHHReport:
            print(hhh + ': ' + str(HHHReport[hhh]))
        return
        
    def report(self, Dict, HHHes):
        """make report to get TCAM counts of HHHes from Dict
        
            Keyword arguments:
            Dict -- a processed dict 
            HHHes -- list of HHHes

        """
    # Dict: from TCAM rules, but after removing
    # not so useful rules
        logging.debug("RepORtinG")
        sumReported = 0 
        report = {}
        for prefix in HHHes:
            logging.debug("HHH prefix "+prefix)
            leftChild = prefix+'0'
            rightChild = prefix+'1'
         
            if self.isLeaf(prefix):
                report[prefix] = Dict[prefix]
            elif self.isRoot(prefix):
                if leftChild in HHHes and rightChild in HHHes:
                    report[prefix] = 0
                elif leftChild in HHHes and rightChild not in HHHes:
                    report[prefix] = Dict[rightChild]
                elif leftChild not in HHHes and rightChild in HHHes:
                   report[prefix] = Dict[leftChild]
                else:
                    report[prefix] = Dict[leftChild] + Dict[rightChild]
            else:
                if (leftChild in Dict and rightChild in Dict):
                    report[prefix] = Dict[leftChild] + Dict[rightChild]
                else:
                    report[prefix] = Dict[prefix]
            logging.debug("report[prefix] "+str(report[prefix]))
        logging.debug("RepORtinG OVER-----------------------")
        return report

    def isLeaf(self, prefix):
        if (len(prefix) > self.leafBits):
            return True
        return False
    
    def isRoot(self, prefix):
        if prefix=='.':
            return True
        else:
            return False

    def getParent(self, prefix):
        return prefix[:-1]


if __name__ == '__main__':
        main()




