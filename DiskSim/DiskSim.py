'''
Created on Apr 14, 2013
DiskSim module - includes main Simulator functionality, implemenation.
Note: all times are in millisecods (ms).
@author: Michael Kepple
'''
from simpy import *
import random
from random import seed, expovariate
import argparse, SCANQueue

from itertools import count


ALGORITHM = None
INTER_ARRIVAL = None
DISK_RPM = None
SECTORS = 128
DISK_REQUESTS = 1000
MEAN_READ_LENGTH = 4
MAXTIME = 100000.0

class SSFQueue(Priority):
    # Constructor
    def __init__(self, maxlen=0):
        super(Priority, self).__init__(maxlen)
        self._data = []
        self._item_id = count()
        
    def push(self, item, priority=0):
        """Push ``item`` with ``priority`` onto the heap, maintain the
        heap invariant.

        A higher value for ``priority`` means a higher priority. The
        default is ``0``.

        """
        print("Track Number: %d\n"%priority)
        print("Read Head Location: %d\n"%self.sim.head.location)
        print("Priority Calculation: %d\n"%abs(priority-self.sim.location))      
        super(SSFQueue, self)._check_push()
        heappush(self._data, (-priority, next(self._item_id), item))
        
class Controller(Process):
    """Disk controller generates DISK_REQUESTS # of requests for read head, 
    distributed uniformly with average interarrival time specified by the user."""
    def generate(self, mean):
        for i in range(DISK_REQUESTS):
            req = ReadRequest(name="Request%03d" % (i), sim=self.sim)
            self.sim.activate(req, req.request())
            nextReq = random.uniform(0, mean*2)
            yield hold, self, nextReq
        
class ReadRequest(Process):
    def request(self):
        arrive = self.sim.now()
        numAhead = len(self.sim.head.waitQ)
        trackNum = random.uniform(0, 100)
        readLength = expovariate(1.0/MEAN_READ_LENGTH)
        print("%s: Arrived @ %8.3f"%(self.name, self.sim.now()))
        
        # trackNum sets priority
        yield request,self,self.sim.head,trackNum
        wait = self.sim.now()-arrive
        # Calculate seek time to track
        readTime = abs(self.sim.head.position -trackNum) * .4
        # Use rotational latency, number of sectors to determine read time once on track
        readTime += (SECTORS/DISK_RPM) * readLength
        self.sim.accessMon.observe(readTime)
        self.sim.head.position = trackNum
        print("%s: Waited %8.3f"%(self.name, wait))
        yield hold,self,readTime
        yield release,self,self.sim.head
        print("%s: Finished %8.3f"%(self.name, self.sim.now()))
        
class DiskSim(Simulation):
    def run(self):
        #print("Algorithm: %s" % args.a)
        #print("Inter-arrival time: %d" % args.i)
        #print("RPMs: %d" % args.r)
        self.initialize()
        self.accessMon = Monitor('Access time (Seek + Rotation)', sim=self)
        if (ALGORITHM == 'FCFS'):
            self.head = Resource(name="ReadHead",qType=FIFO, sim=self)
        elif (ALGORITHM == 'SSF'):
            self.head = Resource(name="ReadHead",qType=SSFQueue, sim=self)
        else:
            self.head = Resource(name="ReadHead", qType=SCANQueue, sim=self)
        self.head.position = 0
        controller = Controller('Controller',sim=self)
        self.activate(controller, controller.generate(mean=INTER_ARRIVAL), at=0.0)
        self.simulate(until=MAXTIME)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Hard Disk Simulation')
    parser.add_argument('-a', choices=['FCFS','SSF','SCAN'],default='SSF', 
        help="""the algorithm used by the read head when selecting the next 
        sector. Choices are FCFS, SSF, or SCAN. Default is FCFS""")
    parser.add_argument('-i', default=5, type=int, help="""average inter-arrival
        times of disk requests. Will be uniformly distributed; default is 150""")
    parser.add_argument('-r', default=7200, type=int, help="""maximum rotations 
        per minute achieveable by the hard disk. Default is 7200""")
    args = parser.parse_args()
    ALGORITHM = args.a
    INTER_ARRIVAL = args.i
    DISK_RPM = args.r
    model = DiskSim()
    model.run()
    # Plot stuff
    Histo = model.accessMon.histogram(low=0.0,high=40.0,nbins=20)
    plt = SimPlot()                                                  
    plt.plotHistogram(Histo,xlab='Time (millisecs)',                       
                  title="Access Time (seek + rotation)",
                  color="red",width=3)                         
    plt.mainloop() 