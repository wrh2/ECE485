"""
    High level implementation of system described for ECE485 project
    
    This implementation utilizes NumPy package to automatically
    unpack the data from the csv files provided by the professor
    into NumPy arrays. To compliment this, the argparse package
    is also used to allow for specifying the csv file names on the
    command line.

    Also the implementation uses the MyHDL package for simulating
    this event driven system.

    Lastly, the randrange function from the random package is
    used for randomizing data supplied to the hub since no actual
    data is specified in the traffic files.

    Programmed by: William Harrington
    Project Team:  Sixty Percent Club
    ECE485 Final Project
"""

# use MyHDL package, allows for high level modeling with delays
from myhdl import *

# use numpy package, give it alias np
# used for reading in the CSV files
import numpy as np

# use argparse package, parses command line arguments
import argparse

# use randrange from random package
# used for randomizing data
from random import randrange

# import isfile function to make sure 
# the csv file provided exists
# import join to join the path if it had 
# any extra characters
from os.path import isfile, join

""" ************Start of program***************** """

# initialize argument parser
parser = argparse.ArgumentParser()

# argument for filename of traffic file
parser.add_argument('-f',
                    action='store',
                    dest='fname',
                    required=True,
                    help='filename'
                    )

# parse the arguments
arguments = parser.parse_args()

# use numpy to load data from csv file
if not isfile(join(arguments.fname)):
    print 'ERROR: %s does NOT exist' % arguments.fname
    exit(1)
columns = np.loadtxt(arguments.fname, dtype=int, delimiter=',', unpack=True)

# put data from csv file into arrays
t = columns[0]       # time
device = columns[1]  # device ID
op = columns[2]      # operation type
ts = columns[3]      # transaction size
tag = columns[4]     # tag


""" cache size options """
# M1 memory, 2 cache lines of 128 kB each
M1 = 2

# M2 memory option 1, 4 cache lines of 128 kB each
M20 = 4

# M2 memory option 2, 1 cache line of 512 kB each
M21 = 1

# M3 memory option 1, 10 cache lines of 128 kB each
M30 = 10

# M3 memory option 2, 2 cache lines of 512 kB each
M31 = 2

# M3 memory option 3, 1 cache line of 1kB each
M32 = 1


""" cache latency specs """
# latency in clock cylces
M1_latency = 1
M2_latency = 8
M3_latency = 15


""" bandwidth delays (in clock cycles) """

# delay for local bit-serial link
# Has 5.5MBits/s capacity which means
# bits must be sent in intervals of
# 1/(5.5*10e6) or 18 clock cycles
bandwidth_delay_local = 18

# delay for satellite bit-serial link
# has 1200 bits/s capacity which means
# bits must be sent in intervals of
# 1/1200 or 83,333 clock cycles
# There is an additional latency of
# 100 clock cycles for communication
# with the satellite, giving us 83,4333 clock cylces
bandwidth_delay_satellite = 83433


""" Data center """

# holds data in the data center
# aka "Main memory"
data_center = {}


class cache:
    """ High level model of cache for hub """

    def __init__(self, max_capacity=M1, latency=M1_latency, policy='FIFO'):
        """
            Initialization, defaults to M1 capacity & latency
            with a FIFO eviction policy.

            Can be easily modified by specifying the following
            arguments when instantiation occurs

            :param input max_capacity: maximum capacity of the cache
            :param input latency: latency of memory in clock cycles
            :param input policy: eviction policy
        """

        # internal memory
        self.m = {}

        # tags array used for tracking FIFO
        self.tags = []

        # hit flag, indicates read/write hit or miss
        self.hit = False

        # keeps track of how full cache is
        self.used = 0

        # maximum capacity of cache
        self.max_capacity = max_capacity

        # full flag, indicates cache is at max capacity
        self.full = False

        # latency of memory
        self.latency = latency

        # 16 bit databus for input output
        self.databus = []

        # performance statistics
        self.hits = 0        # hits
        self.misses = 0      # misses
        self.comm_cost = 0   # communication cost
        self.cum_latency = 0 # cumulative latency
        
        # eviction policy
        if policy == 'FIFO':
            # first in first out
            self.FIFO = True
            self.LRU = False
        elif policy == 'LRU':
            # least recently used
            self.FIFO = False
            self.LRU = True
        else:
            # this just catches bogus init arguments
            # and makes the policy FIFO
            self.FIFO = True
            self.LRU = False

    def checkCapacity(self):
        """
            Check capacity of cache
        """
        if self.used >= self.max_capacity:

            # used exceeds capacity, set full flag
            self.full = True

        else:

            # used doesn't exceed capacity, unset full flag
            self.full = False

    def access(self, w, tag, ts):
        """
            Access the memory

            :param input w: write if 1/read if 0
            :param input tag: tag in cache
            :param input ts:  transaction size
        """

        # keep track of when transaction started
        start = now()

        # delay due to memory latency
        yield delay(self.latency)

        # convert tag to hex
        tag = hex(tag)

        # write
        if w:

            # check to see if tag in memory
            if tag in self.m:

                # tag is in memory
                # set hit flag, increment hits 
                self.hit = True
                self.hits += 1

                # check capacity of cache
                self.checkCapacity()

                # check for full flag, if set, evict
                # also make sure new cache line + used < max_capacity to
                # prevent the cache from being over filled
                # and evict if new cache line + used > max_capacity
                if self.full or (self.used+1 > self.max_capacity):

                    # eviction is needed, check policy
                    if self.LRU:

                        # least recently used
                        old_key = min(self.m.keys(), key=lambda k:self.m[k])

                        # let eviction function take over
                        # resume execution here when done
                        yield self.evict(old_key)

                    elif self.FIFO:

                        # first in first out
                        # let eviction function take over
                        # resume execution here when done
                        yield self.evict(self.tags[-1])

                # initialize cache line
                self.m[tag] = []
                
                # go through the data and grab two bytes
                # and store in memory
                # the tag and index bits take up two bytes
                for x in range(ts/2 - 1):
                    
                    # wait for 16 bits to be sent
                    for y in range(16):

                        # delay due to local link bandwidth
                        yield delay(bandwidth_delay_local)

                    # make word random 4 digit hex value
                    self.m[tag].append(hex(randrange(2**16-1)))

                    # delay due to memory latency
                    yield delay(self.latency)

                # update used
                self.used += 1

            else:

                # tag not in memory
                # unset hit flag, increment misses
                self.hit = False
                self.misses += 1

                # check capacity of cache
                self.checkCapacity()

                # check for full flag, if set, evict
                # also make sure new cache line + used < max_capacity to
                # prevent the cache from being over filled
                # and evict if new cache line + used > max_capacity
                if self.full or (self.used + 1 > self.max_capacity):

                    # eviction is needed, check policy
                    if self.LRU:

                        # least recently used
                        old_key = min(self.m.keys(), key=lambda k:self.m[k])

                        # let eviction function take over
                        # resume execution here when done
                        yield self.evict(old_key)

                    elif self.FIFO:

                        # first in first out
                        # let eviction function take over
                        # resume execution here when done
                        yield self.evict(self.tags[-1])

                if self.FIFO:
                    # insert tag into beginning of tags array
                    self.tags.insert(0, tag)

                # initialize cache line
                self.m[tag] = []

                # go through the data and grab two bytes
                # and store in memory
                # the tag and index bits take up two bytes
                for x in range(ts/2 - 1):

                    # wait for 16 bits to be sent
                    for y in range(16):

                        # delay due to local link bandwidth
                        yield delay(bandwidth_delay_local)

                    # make word random 4 digit hex value
                    self.m[tag].append(hex(randrange(2**16-1)))

                    # delay due to memory latency
                    yield delay(self.latency)

                # update used
                self.used += 1

        # read
        else:

            # check to see if tag is in memory
            if tag in self.m:

                # tag is in memory
                # set hit flag, increment hits
                self.hit = True
                self.hits += 1

                # nice print out to tell us what's going on
                print '%s: Read request hit, receiving bytes from memory' % now()

                # counter for counting the words
                counter = 0

                # go through data in cache line
                for bits in self.m[tag]:

                    # bandwidth delay for local link
                    # and memory latency
                    yield delay(4*(len(bits)-2)*self.latency*bandwidth_delay_local)

                    # output to databus
                    self.databus = bits

                    # nice print out to tell us what's going on
                    print '%s: Word %s = %s' % (now(), counter, self.databus)                  

                    # increment counter
                    counter += 1

            else:

                # tag is not in memory
                # unset hit flag, increment misses
                self.hit = False
                self.misses += 1

                # no output on databus
                # until we get it from the data center
                self.databus = []

                # keep track of when transactions started
                started = now()

                # nice print out to tell us what's up
                print '%s: Read request miss, contacting data center...' % now()
                
                # contact data center, send command via satellite

                # delay for hub to satellite
                yield delay(32*bandwidth_delay_satellite)

                # delay for satellite to data center
                yield delay(32*bandwidth_delay_satellite+100)

                # for counting the words
                counter = 0
                for bits in data_center[tag]:
                    # data center to satellite delay
                    yield delay(4*(len(bits) - 2)*(bandwidth_delay_satellite+100))

                    # satellite to hub delay
                    yield delay(4*(len(bits) - 2)*bandwidth_delay_satellite)
                    
                    # hub to device delay
                    yield delay(4*(len(bits) - 2)*bandwidth_delay_local)

                    # output to databus
                    self.databus = bits

                    # print statement to tell us what's going on
                    print '%s: Word %s = %s' % (now(), counter, self.databus)

                    # increment counter
                    counter += 1

                # change in time from when transaction started to finish
                finished = now() - started

                # awesome print statement to inform user
                print '%s: Done communicating with data center...time elapsed: %s' % (now(), finished)

                # update communication cost
                self.comm_cost += (finished*10e-8)/60

        # memory access done, add to cumulative latency, convert to seconds
        # because who really thinks about this in clock cycles?
        self.cum_latency += (now()-start)*10e-8

    def evict(self, tag):
        """
            Evict cache line

            :param input tag: tag in cache to evict
        """

        # show eviction information
        print '%s: EVICT %s, contacting data center...' % (now(), tag)

        # initialize data center memory line
        data_center[tag] = []

        # keep track of when eviction process started
        started = now()
        
        # eviction about to happen, write to data center
        for bits in self.m[tag]:

            # hub to satellite delay
            yield delay(4*(len(bits) - 2)*bandwidth_delay_satellite)

            # satellite to data center delay
            yield delay(4*(len(bits) - 2)*(bandwidth_delay_satellite+100))

            # store in data center
            data_center[tag].append(bits)

        # change in time from when transaction started to finish
        finished = now() - started

        # is it obvious yet that I like to keep my user informed?
        print '%s: Done communicating with data center...time elapsed: %s' % (now(), finished)

        # update communication cost
        self.comm_cost += (finished*10e-8)/60

        # update used
        self.used -= 1

        # check for fifo
        if self.FIFO:
            # first in first out eviction, evict from tags array & memory
            self.tags.pop(-1)

        # get rid of cache line
        self.m.pop(tag)


# Level 1 memory module, 1 M2 memory with 4 cache lines of 128 Bytes each
L1 = cache(max_capacity=M20, latency=M2_latency)

# Level 2 memory module, 10 M3 memories each with 1 cache line of 1kB
L2 = cache(max_capacity=10*M32, latency=M3_latency)


def hub(mem1, mem2):
    """
        High level modeling of transactions on wireless hub

        :param input mem1: Level 1 memory module
        :param input mem2: Level 2 memory module
    """

    # wait for key press to continue    
    try:
        input("%s: Press enter to start" % now())

    # just pressing enter yields a SyntaxError, make exception
    except SyntaxError:

        # ignore error
        pass

    key = 'A'
    # go through the transactions
    for i in range(len(t)):

        # wait for key press to continue
        if key.upper() != 'Q':
            try:
                key = raw_input("%s: Pause. Press enter for next event or Q to run all events: " % now())

            # just pressing enter yields a SyntaxError, make exception
            except SyntaxError:

                # ignore error
                pass

        # check operation, op = 0 is a SEND
        if not op[i]:

            # some output to tell us what is going on
            print "%s: SEND tag %s size %s" % (now(), tag[i], ts[i])

            # cache's segregated according to transaction size
            # everything that is 128 bytes should be in L1
            # everything else is placed in L2
            if ts[i] > 128:

                # transaction size greater than 128 bytes
                # access L2, check to see if tag in L2
                # first we yield for a small delay due to local link
                # bandwidth limitations then we yield to the memory
                # access and then resume execution at this point
                # once that has finished
                yield delay(16*bandwidth_delay_local)
                yield mem2.access(1, tag[i], ts[i])

            else:

                # transaction size 128 bytes
                # access L1, check to see if tag in L1
                # first we yield for a small delay due to local link
                # bandwidth limitations then we yield to the memory
                # access and then resume execution at this point
                # once that has finished
                yield delay(16*bandwidth_delay_local)
                yield mem1.access(1, tag[i], ts[i])

            # transaction is finished
            print "%s: SENT tag %s size %s" % (now(), tag[i], ts[i])

        # op = 1, we have a REQUEST
        else:

            # some output to tell us what is going on
            print "%s: REQUEST tag %s" % (now(), tag[i])

            # cache's segregated according to transaction size
            # everything that is 128 bytes should be in L1
            # everything else is placed in L2
            if ts[i] > 128:

                # transaction size greater than 128 bytes
                # access L2, check to see if tag in L2
                # first we yield for a small delay due to local link
                # bandwidth limitations then we yield to the memory
                # access and then resume execution at this point
                # once that has finished
                yield delay(16*bandwidth_delay_local)
                yield mem2.access(0, tag[i], ts[i])

            else:

                # transaction size 128 bytes
                # access L1, check to see if tag in L1
                # first we yield for a small delay due to local link
                # bandwidth limitations then we yield to the memory
                # access and then resume execution at this point
                # once that has finished
                yield delay(16*bandwidth_delay_local)
                yield mem1.access(0, tag[i], ts[i])

            # transaction finished, check hit flag on L1 & L2 cache
            if mem1.hit:

                # L1 indicates hit
                print "%s REQUEST fulfilled by L1" % now()
                mem1.hit = False

            elif mem2.hit:

                # L2 indicates hit
                print "%s REQUEST fulfilled by L2" % now()
                mem2.hit = False

    # simulation done, show stats
    print '--------------------------------------'            
    print '%s: Simulation finished. Showing stats' % now()
    print 'L1 Hits: %s, L1 Misses: %s' % (mem1.hits, mem1.misses)
    print 'L2 Hits: %s, L2 Misses: %s' % (mem2.hits, mem2.misses)
    print 'Cumulative latency: %3.2f seconds' % (mem1.cum_latency + mem2.cum_latency)
    print 'Total communication cost: $%3.2f' % (mem1.comm_cost + mem2.comm_cost)
    print '--------------------------------------'

def main():
    """ Main function """

    # instantiate hub with L1 & L2 caches
    link = hub(L1, L2)

    # return local generator for simulation
    return link

# using MyHDL simulation environment, give it main
sim = Simulation(main())

# run simulation
sim.run()

""" ************End of program***************** """
