'''
Created on Apr 21, 2013

@author: michael
'''
# as for namespace changes
from SimPy.Simulation import *
import Main as Simulation
import ReadRequest


class Controller(Process):
    """Disk controller generates 1000 requests for read head, distributed
    uniformly with average inter-arrival time specified by the user."""
    def generate(self, mean, head):
        for i in range(1000):
            req = ReadRequest(name="Request%03d" % (i))
            activate(req, req.request())
            nextReq = random.uniform(0, mean*2)
            print("Algorithm: %s" % Simulation.ALGORITHM)
            yield hold, self, nextReq