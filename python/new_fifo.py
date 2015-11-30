"""
High level implementation of memories available for ECE485 project
Programmed by William Harrington
ECE485
"""
from myhdl import *  # use MyHDL package
import numpy as np   # use numpy package, give it alias np
import argparse      # use argparse package

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
columns = np.loadtxt(arguments.fname, dtype=int, delimiter=',', unpack=True)

# put data from csv file into arrays
t = columns[0]       # time
device = columns[1]  # device ID
op = columns[2]      # operation type
ts = columns[3]      # transaction size
tag = columns[4]     # tag


# size in bytes
M1 = 256
M2 = 512
M3 = 1024

# latency in clock cylces
M1_latency = 1
M2_latency = 8
M3_latency = 15

# bandwidth delay in clock cycles
bandwidth_delay_local = 18


class cache:
    """ High level model of M1 memory """

    def __init__(self, max_capacity=M1, latency=M1_latency):
        """
            M1 initialization

            :param input max_capacity: maximum capacity of the cache
            :param input latency: latency of memory in clock cycles
        """

        # memory
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

    def checkCapacity(self):
        """
            Check capacity of cache
        """
        if self.used >= self.max_capacity:
            self.full = True
        else:
            self.full = False

    def access(self, w, tag, ts):
        """
            Access the memory

            :param input tag: tag in cache
            :param input ts:  transaction size
        """

        yield delay(self.latency)
        # yield delay(self.latency*ts)

        # write
        if w:

            # check to see if tag in memory
            if tag in self.m:

                # set hit flag
                self.hit = True

                # check capacity of cache
                self.checkCapacity()

                # check for full flag, if set, evict
                # also make sure ts + used < max_capacity to
                # prevent the cache from being over filled
                # and evict if ts + used > max_capacity
                if self.full or (ts+self.used > self.max_capacity):

                    # eviction is needed
                    self.evict(self.tags[-1])

                # convert to binary
                # ex: transaction size = 128
                # intbv(256-1) will yield 8 bits of 1 aka one byte
                # multiplying this by 128 will give us 128 bytes
                self.m[tag] = ts*bin(intbv(255))

                # update used
                self.used += ts

            # tag no in memory
            else:

                # unset hit flag
                self.hit = False

                # check capacity of cache
                self.checkCapacity()

                # check for full flag, if set, evict
                # also make sure ts + used < max_capacity to
                # prevent the cache from being over filled
                # and evict if ts + used > max_capacity
                if self.full or (ts+self.used > self.max_capacity):

                    # eviction is needed
                    self.evict(self.tags[-1])

                # insert tag into beginning of tags array
                self.tags.insert(0, tag)

                # convert to binary
                # ex: transaction size = 128
                # intbv(256-1) will yield 8 bits of 1 aka one byte
                # multiplying this by 128 will give us 128 bytes
                self.m[tag] = ts*bin(intbv(255))

                # update used
                self.used += ts

        # read
        else:

            # check to see if tag is in memory
            if tag in self.m:

                # set hit flag
                self.hit = True

                # tracker variable for loop below
                lastBits = 0

                # TODO: this should happen multiple times
                # got a hit, output 2 bytes on databus
                for bits in range(len(self.m[tag])):

                    # every two bytes
                    if bits % 16 == 0:

                        # output to databus
                        self.databus = self.m[tag][lastBits:bits]

                        # update lastBits
                        lastBits = bits

                    # bandwidth delay for local link
                    yield delay(self.latency*bandwidth_delay_local)

            # tag is not in memory
            else:

                # unset hit flag
                self.hit = False

                # output 0's on databus
                self.databus = bin(intbv(0))

                # TODO: contact data center
                # yield delay()

    def evict(self, tag):
        """
            Evict cache line

            :param input tag: tag in cache to evict
        """

        # show eviction information
        print '%s: EVICT %s' % (now(), tag)

        # count the bytes getting evicted
        countByte = 0
        for bits in range(len(self.m[tag])):
            if bits % 8 == 0:
                countByte += 1
        size = countByte

        # update used
        self.used -= size

        # first in first out eviction, evict from tags array & memory
        self.tags.pop(-1)
        self.m.pop(tag)


L1 = cache(max_capacity=M1)
L2 = cache(max_capacity=10*M3, latency=M3_latency)


def operations(mem1, mem2):

    for i in range(len(t)):

        if not op[i]:
            # some output to tell us what is going on
            print "%s: SEND tag %s size %s" % (now(), tag[i], ts[i])

            if ts[i] > 128:
                yield mem2.access(1, tag[i], ts[i])
            else:
                # let the send transaction happen
                yield mem1.access(1, tag[i], ts[i])

            # transaction is finished
            print "%s: SENT tag %s size %s" % (now(), tag[i], ts[i])

        # op = 1, we have a REQUEST
        else:

            # some output to tell us what is going on
            print "%s: REQUEST tag %s" % (now(), tag[i])

            yield mem1.access(0, tag[i], ts[i])
            yield mem2.access(0, tag[i], ts[i])

            if mem1.hit:
                # transaction is finished
                print "%s REQUEST fulfilled by mem1, got %s" % (now(),
                                                                mem1.databus)

            elif mem2.hit:

                print "%s REQUEST fulfilled by mem2, got %s" % (now(),
                                                                mem2.databus)


def main():
    """ Main function """
    # instance of users, give them an instance of the wireless hub
    ops = operations(L1, L2)

    # return local generator for simulation
    return ops

# using MyHDL simulation environment, give it main
sim = Simulation(main())

# run simulation
sim.run()
