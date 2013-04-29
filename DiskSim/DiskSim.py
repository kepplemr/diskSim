'''
 Module:    DiskSim - includes main Simulator functionality, implementation.
Created:    14 Apr 2013
  Notes:    all times are in millisecods (ms).
   Uses:    Python 3.2
            SimPy 2.3.1
@author:    Michael Kepple
'''
from SimPy.Simulation import *
import random
from random import seed, expovariate
import argparse
from ReadQueue import *

from itertools import count

INTER_ARRIVAL = None
DISK_RPM = None
ALGORITHM = None
SECTORS = 128
DISK_REQUESTS = 5
MEAN_READ_LENGTH = 4
MAXTIME = 100000.0
        
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
        self.trackNum = int(random.uniform(0, 100))
        print("Assign track num: %d"%self.trackNum)
        readLength = expovariate(1.0/MEAN_READ_LENGTH) 
        print("%s: Arrived @ %8.3f"%(self.name, self.sim.now()))
        # Pushes shit onto queue
        yield request,self,self.sim.head,self.trackNum
        wait = self.sim.now()-arrive
        readTime = abs(self.sim.head.pos - self.trackNum) * .4
        self.sim.head.pos = self.trackNum
        # Use rotational latency, number of sectors to determine read time once on track
        readTime += (SECTORS/DISK_RPM) * readLength
        self.sim.accessMon.observe(readTime)
        print("%s: Waited %8.3f"%(self.name, wait))
        yield hold,self,readTime
        # Pops shit off of queue
        yield release,self,self.sim.head
        print("%s: Finished %8.3f"%(self.name, self.sim.now()))

class DiskSim(Simulation):
    def run(self):
        self.initialize()
        self.accessMon = Monitor('Access time (Seek + Rotation)', sim=self)
        self.head = Resource(name="ReadHead",qType=ReadQ, sim=self)
        self.head.algorithm = ALGORITHM
        self.head.pos = 0
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