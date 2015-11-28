"""
  High level modeling and static simulation 
  for ECE485 final project
  Programmed by William Harrington
"""
from myhdl import * # use MyHDL package
import numpy as np  # use numpy package, give it alias np
import argparse     # use argparse package

# initialize argument parser
parser = argparse.ArgumentParser()

# argument for getting mood of Einstein
parser.add_argument('-f', action = 'store', dest = 'fname', required = True, help = 'filename')

# parse the arguments
arguments = parser.parse_args()

# use numpy to load data from csv file
columns = np.loadtxt(arguments.fname, dtype=int, delimiter=',', unpack=True)

# put data from csv file into arrays
t = columns[0]       # time
device = columns[1]  # device ID
op = columns[2]      # operation type
ts = columns[3]      # transaction size
tag = columns[4]     # tag

class hub:
    """ Wireless hub object """
    
    # memory
    mem = {}

    # output
    item = None

    # memory latency
    latency = 18*16
    
    # satellite latency    
    sat_latency = 150*16*83333

    # variable for capacity
    capacity = 0

    # max
    max_capacity = 10496

    # memory full flag
    full = False

    # list of keys, for eviction policy
    keys = []

    def send(obj, tag, ts):
        """ Send function
            :param input obj: class input, should be queue class
            :param input tag: tag for memory
            :param input ts:  transaction size
        """
        # memory latency
        yield delay(obj.latency*ts)
        
        # check is tag in cache
        if tag in obj.mem:

            # got a hit
            print '%s: SEND hit' % now()

            # are we full tho, yeah we full
            if obj.full:

                # output tag as its getting evicted
                obj.item = keys[-1]
            
                # process eviction
                print "%s: EVICT tag %s size %s, " % (now(), obj.keys[-1], obj.mem[tag])
            
                # update capacity, get rid of that cache line
                obj.capacity -= obj.mem.pop(obj.keys[-1])['ts']
            
                # clean up keys list
                obj.keys.pop(len(keys)-1)
            
                # set cache line
                obj.mem[tag] = {'ts': ts}
            
                # write to data center, long latency here
                yield delay(obj.sat_latency*ts)

            # not full
            else:
                obj.capacity -= obj.mem[tag]['ts'] # get rid of old

                obj.mem[tag] = {'ts': ts} # update memory

                obj.capacity += ts # update capacity

        # tag not in cache
        else:

            # miss
            print '%s: SEND Miss' % now()

            # update memory
            obj.mem[tag] = {'ts': ts}

            # update capacity
            obj.capacity += ts

            # put in list of keys
            obj.keys.insert(0, tag)
            
        #obj.mem[tag] = {'ts': ts}
        #obj.capacity += ts
        print obj.capacity
        #obj.keys.insert(0, tag)

#        # check for tag in memory, make sure not full
#        if tag in obj.mem and not obj.full:
#
#            # put tag in keys list
#            obj.keys.insert(0, tag)
#
#            # put in memory
#            obj.mem[tag] = {'ts': ts}
#            
#            # update capacity
#            obj.capacity += ts
#            print obj.capacity
#
#            # check to see if full
#            if obj.capacity == obj.max_capacity:
#                # capacity reached, set flag
#                obj.full = True
#
#        # check for tag in memory, we're full, eviction imminent
#        elif tag in obj.mem and obj.full:
#
#            # output tag as its getting evicted
#            obj.item = keys[-1]
#            
#            # process eviction
#            print "%s: EVICT tag %s size %s, " % (now(), obj.keys[-1], obj.mem[tag])
#            
#            # update capacity, get rid of that cache line
#            obj.capacity -= obj.mem.pop(obj.keys[-1])['ts']
#            
#            # clean up keys list
#            obj.keys.pop(len(keys)-1)
#            
#            # set cache line
#            obj.mem[tag] = {'ts': ts}
#            
#            # write to data center, long latency here
#            yield delay(obj.sat_latency*ts)
#            
#        # not in memory yet
#        else:
#
#            # write to memory
#            obj.mem[tag] = {'ts': ts}

    def request(obj, tag, ts):
        """ Request function
            :param input obj: class input, should be queue class
            :param input tag: tag for memory
            :param input ts:  transaction size
        """
        
        # memory latency
        yield delay(obj.latency*ts)        
        
        # check if in memory
        if tag in obj.mem:

            print 'REQUEST Hit'
            
            # output from memory
            obj.item = obj.mem[tag]
            
        else:
            
            print 'REQUEST Miss'
            
            yield delay(obj.sat_latency*ts)
            
            obj.mem[tag] = {'ts': ts}
            
            obj.item = obj.mem[tag]

# instance of wireless hub
h = hub()

def Producer(h):
    
    # iterate  
    for i in range(len(t)):
        yield delay(t[i])
        if not op[i]:
            print "%s: SEND tag %s size %s" % (now(), tag[i], ts[i])
            yield h.send(tag[i], int(ts[i]/2))
            print "%s: SENT tag %s size %s" % (now(), tag[i], ts[i])
        else:
            print "%s: REQUEST tag %s" % (now(), tag[i])
            yield h.request(tag[i], int(ts[i]/2))
            print "%s REQUEST fulfilled, got %s" % (now(), h.item)

def main():
    P = Producer(h)
    return P

sim = Simulation(main())
sim.run()
