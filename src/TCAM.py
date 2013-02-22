#!/usr/bin/env python
# encoding: ASCII
import logging
import sys
import os
logging.basicConfig()#level=logging.DEBUG)

class TCAM: 
   
# {'.0': 16, '.010': 12, '.000': 12, '.': 0}

    def philter(self, counts, TCAMList, ipsInBin=False):
        TCAMDict = {}
        
        #initialize counts to 0 so rules always in TCAMDict
        for prefix in TCAMList:
            TCAMDict[prefix] = 0
        
        TCAMList.sort(reverse=True, key=len)
        total = 0
        for ip in counts.keys():
            count = counts[ip]
            logging.debug("ip " + ip)
            for prefix in TCAMList:
                logging.debug("against prefix " + prefix)
                if ipsInBin:
                    ipstr = ip[:len(prefix)]
                else:
                    ipstr = str('.'+self.binary(ip))[:len(prefix)]
                logging.debug("comparing " + str(ipstr) +" and " + str(prefix))
                
                if ipstr == prefix:
                    TCAMDict[prefix] += count
                    total += count
                    break
        if sum(counts.values()) != sum(TCAMDict.values()):
            print("TCAM counting error")    
            
        return TCAMDict

    def binary(self, ip):
        octets = ip.split(".")
        binary = ''.join(bin(int(octets[num]))[2:].zfill(8) for num in range(len(octets)))
        return binary
    
 



