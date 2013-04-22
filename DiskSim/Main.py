'''
Created on Apr 14, 2013

@author: michael
'''
import argparse

ALGORITHM = None
INTER_ARRIVAL = None
DISK_RPM = None
DISK_REQUESTS = 1000
MEAN_READ_LENGTH = 4

# will need to override PriorityQ with an ElevatorQ for that algorithm

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Hard Disk Simulation')
    parser.add_argument('-a', choices=['FCFS','SSF','SCAN'],default='FCFS', 
        help="""the algorithm used by the read head when selecting the next 
        sector. Choices are FCFS, SSF, or SCAN. Default is FCFS""")
    parser.add_argument('-i', default=150, type=int, help="""average inter-arrival
        times of disk requests. Will be uniformly distributed; default is 150""")
    parser.add_argument('-r', default=7200, type=int, help="""maximum rotations 
        per minute achieveable by the hard disk. Default is 7200""")
    args = parser.parse_args()
    ALGORITHM = args.a
    INTER_ARRIVAL = args.i
    DISK_RPM = args.r
    print("Algorithm: %s" % args.a)
    print("Inter-arrival time: %d" % args.i)
    print("RPMs: %d" % args.r)
    
    
    
    
   
            