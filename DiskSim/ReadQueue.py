'''
 Module:    ReadQueue - implementation of read head queue'ing according to
                        algorithm.
Created:    14 Apr 2013
  Notes:    all times are in millisecods (ms).
   Uses:    Python 2.7
            SimPy 2.3.1
            numpy 1.7.1
            matplotlib 1.2.1 (no support for Python 3+)
@author:    Michael Kepple
'''
from SimPy.Lib import *

MAX_PRIORITY = 200

# Creates enum functionality
def enum(**enums):
    return type('Enum', (), enums)

Dir = enum(FORWARD=1, BACK=2)

class ReadQ(Queue):
    """ReadQueue simulates the internal request queue'ing capabilities of the
    heard disk read head. Queues used and priority depend on specified 
    algorithm"""
    def __init__(self, res, moni):
        """Constructor for ReadQ data structure"""
        self.direction = Dir.FORWARD
        Queue.__init__(self, res, moni)

    def enter(self, obj):
        """Add a read request to the waiting queue. Called by Simulator."""
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
        algorithm. Called by Simulator."""
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
        ele = self.pop(0)
        if self.monit:
            self.moni.observe(len(self),t = self.moni.sim.now())
        return ele