'''
Created on Apr 28, 2013

@author: michael
'''
from SimPy.Lib import *
import DiskSim as SIM

MAX_PRIORITY = 200

def enum(**enums):
    return type('Enum', (), enums)

Dir = enum(FORWARD=1, BACK=2)

class ReadQ(Queue):
    def __init__(self, res, moni):
        """Constructor for ReadQ data structure"""
        self.direction = Dir.FORWARD
        FIFO.__init__(self, res, moni)

    def enter(self, obj):
        """Add a read request to the waiting queue"""
        self.append(obj)
        if self.monit:
            self.moni.observe(len(self),t = self.moni.sim.now())
    
    def scanDistance(self, read):
        """Prioritizes reads according to the SCAN/ELEVATOR algorithm"""
        if (self.direction == Dir.FORWARD):
            if (self.resource.pos > read.trackNum):
                return (MAX_PRIORITY-read.trackNum)
            return read.trackNum
        elif (self.direction == Dir.BACK):
            if (self.resource.pos < read.trackNum):
                return (MAX_PRIORITY+read.trackNum)
            return -read.trackNum
    
    def leave(self):
        """Determines which read to service next according to algorithm, and 
        returns it. Changes the direction of reads when appropriate for SCAN
        algorithm"""
        print("Read Head @: %d"%self.resource.pos)
        print("What's in the list:")
        for item in self:
            print("TrackNum: %d"%item.trackNum)
        if (self.resource.algorithm == 'SSF'):
            self.sort(key=lambda read: abs(read.trackNum-self.resource.pos))
        elif (self.resource.algorithm == 'SCAN'):
            if (self.direction == Dir.FORWARD):
                self.sort(key=self.scanDistance)
                if (self.resource.pos > self[0].trackNum):
                    self.direction = Dir.BACK
            elif (self.direction == Dir.BACK):
                self.sort(key=self.scanDistance)
                if (self.resource.pos < self[0].trackNum):
                    self.direction = Dir.FORWARD
        print("What's in the list now:")
        for item in self:
            print("TrackNum: %d"%item.trackNum)
        input()
        ele = self.pop(0)
        if self.monit:
            self.moni.observe(len(self),t = self.moni.sim.now())
        return ele