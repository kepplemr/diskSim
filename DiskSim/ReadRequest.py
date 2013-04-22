'''
Created on Apr 22, 2013

@author: michael
'''
from SimPy.Simulation import *
#
class ReadRequest(Process):
    def request(self):
        nm = Resource(qType=PriorityQ)
        
    