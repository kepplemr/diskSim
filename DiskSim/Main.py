'''
Created on Apr 14, 2013

@author: michael
'''
from SimPy.Simulation import *
from SimPy.SimPlot import *
from random import expovariate, seed

class DiskRequests(Process):
    """ Generator PEM that simulates disk requests """
    def requests(self, numRequests, rate):
        for i in range(numRequests):
            print(i)
            
            