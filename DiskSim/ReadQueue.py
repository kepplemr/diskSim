'''
Created on Apr 28, 2013

@author: michael
'''
from SimPy.Lib import *
import DiskSim as SIM

class ReadQ(FIFO):
    # This method ran only at the beginning of simulation; all Processes will be
    #  on the Queue before we start executing and removing any. 
    # _priority is automatically set to the 4th argument when there is one, don't
    # really need to use it per se. 
    def enter(self, obj):
        if len(self):
            # Higher numerical priority = higher priority
            # In Python, a negative index accesses elements from the end of the
            #   list counting backwards. The last element of a non-empty list is
            #   foo[-1].
            # So, this is saying if the last element has higher priority than the
            #   element we're adding, append the element to the end and be done.
            if self[-1].trackNum >= obj.trackNum:
                self.append(obj)
            else:
                iterator = 0
                while self[iterator].trackNum >= obj.trackNum:
                    iterator += 1
                self.insert(iterator, obj)
        else:
            self.append(obj)
        if self.monit:
            self.moni.observe(len(self),t = self.moni.sim.now())
            
    def leave(self):
        #print("Read Head @: %d"%self.resource.pos)
        #print("What's in the list:")
        #for item in self:
        #    print("TrackNum: %d"%item.trackNum)
        if (self.resource.algorithm == 'SSF'):
            self.sort(key=lambda read: abs(read.trackNum-self.resource.pos))
        elif (self.resource.algorithm == 'SCAN'):
            self.sort()
        #print("What's in the list now:")
        #for item in self:
        #    print("TrackNum: %d"%item.trackNum)
        input()
        ele = self.pop(0)
        if self.monit:
            self.moni.observe(len(self),t = self.moni.sim.now())
        return ele
    