'''
 Module:    DiskSim - includes main Simulator functionality, implementation.
Created:    14 Apr 2013
  Notes:    all times are in millisecods (ms).
   Uses:    Python 2.7
            SimPy 2.3.1
            numpy 1.7.1
            matplotlib 1.2.1 (no support for Python 3+)
@author:    Michael Kepple
'''
from SimPy.Simulation import *
from random import expovariate
import argparse
import ReadQueue
import numpy as np
import matplotlib.pyplot as plt

MOV_TIME = .4
NUM_ALGS = 3
NUM_TESTS = 4
BYTES_PER_SEC = 256
SECTORS = 128
DISK_REQUESTS = 1000
MEAN_READ_LENGTH = 4
MAXTIME = 1000000.0
        
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
    """ReadRequest class simulates a disk head read request sent to the arm"""
    def request(self):
        self.trackNum = int(random.uniform(0, 100))
        readLength = expovariate(1.0/MEAN_READ_LENGTH)
        self.sim.byteMon.observe(readLength*BYTES_PER_SEC)
        yield request,self,self.sim.head,self.trackNum
        trackDis = abs(self.sim.head.pos - self.trackNum)
        self.sim.diskMov.observe(trackDis)
        seekTime = trackDis * MOV_TIME
        self.sim.seekMon.observe(seekTime)
        self.sim.head.pos = self.trackNum
        rotTime = (float(SECTORS)/float(self.sim.head.diskRpm)) * readLength
        self.sim.rotMon.observe(rotTime)
        accessTime = seekTime + rotTime
        self.sim.accessMon.observe(accessTime)
        yield hold,self,accessTime
        yield release,self,self.sim.head

class DiskSim(Simulation):
    """Main Simulation class. Accepts command line input from the user, specifying
    which algorithm to run, the average inter arrival time, and the maximum rpm 
    speed of the disk. Optionally, a test mode can be invoked to test all variants
    and graphically display their results.
    Usage from command line:
    python DiskSim.py -a FCFS -i 25 -r 7000
    ---
    python DiskSim.py -test True
    """
    def __init__(self):
        """Constructor for DiskSim simulation"""
        parser = argparse.ArgumentParser(description='Hard Disk Simulation')
        parser.add_argument('-test',default=False,help="""test mode will run through
        the 12 standard test for the disk simulator.""")
        parser.add_argument('-a', choices=['FCFS','SSF','SCAN'],default='SCAN', 
        help="""the algorithm used by the read head when selecting the next 
        sector. Choices are FCFS, SSF, or SCAN. Default is FCFS""")
        parser.add_argument('-i', default=5, type=int, help="""average inter-arrival
        times of disk requests. Will be uniformly distributed; default is 150""")
        parser.add_argument('-r', default=7200, type=int, help="""maximum rotations 
        per minute achieveable by the hard disk. Default is 7200""")
        args = parser.parse_args()
        if (args.test):
            runTests()
        print("\nAlgorithm: %s"%args.a)
        print("Inter-arrival: %d"%args.i)
        print("Disk RPM: %d"%args.r)
        self.initialize()
        self.accessMon = Monitor('Access time (Seek + Rotation)', sim=self)
        self.seekMon = Monitor('Seek time', sim=self)
        self.rotMon = Monitor('Rotational latency monitor', sim=self)
        self.diskMov = Monitor('Disk arm movement', sim=self)
        self.byteMon = Monitor('Total bytes read', sim=self)
        self.head = Resource(name="ReadHead",qType= ReadQueue.ReadQ, sim=self)
        self.head.algorithm = args.a
        self.head.diskRpm = args.r
        self.head.pos = 0
        controller = Controller('Controller',sim=self)
        self.activate(controller, controller.generate(mean=args.i), at=0.0)
        self.simulate(until=MAXTIME)
        print("Average seek time: %f" %self.seekMon.mean())
        print("Average rotational latency: %F"%self.rotMon.mean())
        print("Average access time: %f"%self.accessMon.mean())
        print("Total seek time: %f"%self.accessMon.total())
        print("Total disk arm movement: %d"%self.diskMov.total())
        print("Throughput: %f"%(self.byteMon.total()/self.now()))
        print("Total execution time: %f"%self.now())

def runTests():
    """Testing method invoked from user command line option. Tests all the
    algorithms with all possible standard specifications and displays results
    to the command line. Also provides a graphical representation of test 
    results."""
    sims = []
    rects = []
    sys.argv=['DiskSim', '-a', 'FCFS', '-i','150', '-r','10000']
    sims.append(DiskSim())
    sys.argv=['DiskSim', '-a', 'SSF', '-i','150', '-r', '10000']
    sims.append(DiskSim())
    sys.argv=['DiskSim', '-a','SCAN', '-i','150', '-r', '10000']
    sims.append(DiskSim())
    sys.argv=['DiskSim', '-a', 'FCFS', '-i','150', '-r','7200']
    sims.append(DiskSim())
    sys.argv=['DiskSim', '-a', 'SSF', '-i','150', '-r', '7200']
    sims.append(DiskSim())
    sys.argv=['DiskSim', '-a','SCAN', '-i','150', '-r', '7200']
    sims.append(DiskSim())
    sys.argv=['DiskSim', '-a', 'FCFS', '-i','5', '-r','10000']
    sims.append(DiskSim())
    sys.argv=['DiskSim', '-a', 'SSF', '-i','5', '-r', '10000']
    sims.append(DiskSim())
    sys.argv=['DiskSim', '-a','SCAN', '-i','5', '-r', '10000']
    sims.append(DiskSim())
    sys.argv=['DiskSim', '-a', 'FCFS', '-i','5', '-r','7200']
    sims.append(DiskSim())
    sys.argv=['DiskSim', '-a', 'SSF', '-i','5', '-r', '7200']
    sims.append(DiskSim())
    sys.argv=['DiskSim', '-a','SCAN', '-i','5', '-r', '7200']
    sims.append(DiskSim())
    ind = np.arange(4)
    width = 0.30
    fig = plt.figure()
    ax = fig.add_subplot(111)
    f_res = [[]*NUM_TESTS for x in xrange(NUM_ALGS)]
    s_res = [[]*NUM_TESTS for x in xrange(NUM_ALGS)]
    e_res = [[]*NUM_TESTS for x in xrange(NUM_ALGS)]
    for i in range(4):
        f_res[0].append(sims[(NUM_ALGS*i+0)].seekMon.mean())
        f_res[1].append(sims[(NUM_ALGS*i+0)].rotMon.mean())
        f_res[2].append(sims[(NUM_ALGS*i+0)].byteMon.total()/sims[(NUM_ALGS*i+0)].now())
        s_res[0].append(sims[(NUM_ALGS*i+1)].seekMon.mean())
        s_res[1].append(sims[(NUM_ALGS*i+1)].rotMon.mean())
        s_res[2].append(sims[(NUM_ALGS*i+1)].byteMon.total()/sims[(3*i+1)].now())
        e_res[0].append(sims[(NUM_ALGS*i+2)].seekMon.mean())
        e_res[1].append(sims[(NUM_ALGS*i+2)].rotMon.mean())
        e_res[2].append(sims[(NUM_ALGS*i+2)].byteMon.total()/sims[(NUM_ALGS*i+2)].now())
    rects.append(ax.bar((ind+width), f_res[0], width, color='red'))
    rects.append(ax.bar((ind+width*2), s_res[0], width, color='green'))
    rects.append(ax.bar((ind+width*3), e_res[0], width, color='blue'))
    ax.set_ylabel('Milliseconds')
    ax.set_title('Average Seek Time')
    ax.set_xticks(ind+width*2)
    ax.set_xticklabels(('150/10000','150/7200','5/10000','5/7200'))
    ax.legend((rects[0][0],rects[1][0],rects[2][0]), ('FCFS', 'SSF','Elevator/SCAN'))
    plt.show()
    # Rotational Latency Display
    fig = plt.figure()
    ax = fig.add_subplot(111)
    rects.append(ax.bar((ind+width), f_res[1], width, color='red'))
    rects.append(ax.bar((ind+width*2), s_res[1], width, color='green'))
    rects.append(ax.bar((ind+width*3), e_res[1], width, color='blue'))
    ax.set_ylabel('Milliseconds')
    ax.set_title('Average Rotational Latency')
    ax.set_xticks(ind+width*2)
    ax.set_xticklabels(('150/10000','150/7200','5/10000','5/7200'))
    ax.legend((rects[0][0],rects[1][0],rects[2][0]), ('FCFS', 'SSF','Elevator/SCAN'))
    plt.show()
    # Throughput Display
    fig = plt.figure()
    ax = fig.add_subplot(111)
    rects.append(ax.bar((ind+width), f_res[2], width, color='red'))
    rects.append(ax.bar((ind+width*2), s_res[2], width, color='green'))
    rects.append(ax.bar((ind+width*3), e_res[2], width, color='blue'))
    ax.set_ylabel('Milliseconds')
    ax.set_title('Average Throughput')
    ax.set_xticks(ind+width*2)
    ax.set_xticklabels(('150/10000','150/7200','5/10000','5/7200'))
    ax.legend((rects[0][0],rects[1][0],rects[2][0]), ('FCFS', 'SSF','Elevator/SCAN'))
    plt.show()

if __name__ == "__main__":
    DiskSim()