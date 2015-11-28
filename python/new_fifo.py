"""
  High level modeling and static simulation
  for ECE485 final project
  Programmed by William Harrington
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


class hub:
    """ Model of Wireless hub as an object """

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
            :param input obj: class input, should be hub class
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
                print "%s: EVICT tag %s size %s, " % (now(),
                                                      obj.keys[-1],
                                                      obj.mem[tag])

                # update capacity, get rid of that cache line
                obj.capacity -= obj.mem.pop(obj.keys[-1])['ts']

                # clean up keys list
                obj.keys.pop(len(keys)-1)

                # set cache line
                obj.mem[tag] = {'ts': ts}

                # update capacity
                obj.capacity += ts

                if obj.capacity == obj.max_capacity:
                    obj.full = True

                # write to data center, long latency here
                yield delay(obj.sat_latency*ts)

            # not full
            else:

                # lets see if its the same transaction now
                # we only do something if it isn't
                if obj.mem[tag]['ts'] != ts:

                    # get rid of old
                    obj.capacity -= obj.mem[tag]['ts']

                    # update memory
                    obj.mem[tag] = {'ts': ts}

                    # update capacity
                    obj.capacity += ts

                    # check if capacity reached
                    if obj.capacity == obj.max_capacity:

                        # capacity reached, set flag
                        obj.full = True

        # tag not in cache
        else:

            # miss
            print '%s: SEND Miss' % now()

            # update memory
            obj.mem[tag] = {'ts': ts}

            # update capacity
            obj.capacity += ts

            if obj.capacity == obj.max_capacity:
                    obj.full = True

            # put in list of keys
            obj.keys.insert(0, tag)

    def request(obj, tag, ts):
        """ Request method

            :param input obj: class input, should be hub class
            :param input tag: tag for memory
            :param input ts:  transaction size
        """

        # memory latency
        yield delay(obj.latency*ts)

        # check if in memory
        # if in memory
        if tag in obj.mem:

            # debug message, gonna get rid of this later
            # got a hit
            print '%s: REQUEST Hit' % now()

            # output from memory
            obj.item = obj.mem[tag]

        # not in memory
        else:

            # big ol miss, debug message
            print '%s: REQUEST Miss' % now()

            # gotta get it from the data center
            yield delay(obj.sat_latency*ts)

            # check to see if memory is full
            # evict a line if memory is full
            if obj.full:

                # output tag as its getting evicted
                obj.item = keys[-1]

                # process eviction
                print "%s: EVICT tag %s size %s, " % (now(),
                                                      obj.keys[-1],
                                                      obj.mem[tag]
                                                      )

                # update capacity, get rid of that cache line
                obj.capacity -= obj.mem.pop(obj.keys[-1])['ts']

                # clean up keys list
                obj.keys.pop(len(keys)-1)

                # set cache line
                obj.mem[tag] = {'ts': ts}

                # update capacity
                obj.capacity += ts

                # check if capacity reached
                if obj.capacity == obj.max_capacity:

                    # capacity reached, set flag
                    obj.full = True

                # evicted line has to go to data center
                # long latency here
                yield delay(obj.sat_latency*ts)

            # memory is not full
            else:

                # set cache line
                obj.mem[tag] = {'ts': ts}

                # update capacity
                obj.capacity += ts

                # check to see if capacity reached
                if obj.capacity == obj.max_capacity:

                    # capacity reached, set flag
                    obj.full = True

                # output item
                obj.item = obj.mem[tag]

# instance of wireless hub
h = hub()


def users(h):

    # iterate through each item in the csv data
    for i in range(len(t)):

        # delay by time at which transactions happens
        # for instance if t[i] = 50, adds 50 to the
        # end of the last transaction
        yield delay(t[i])

        # check the command, op = 0 is a SEND, op = 1 is a REQUEST

        # op = 0, we have a SEND
        if not op[i]:

            # some output to tell us what is going on
            print "%s: SEND tag %s size %s" % (now(), tag[i], ts[i])

            # let the send transaction happen
            yield h.send(tag[i], int(ts[i]/2))

            # transaction is finished
            print "%s: SENT tag %s size %s" % (now(), tag[i], ts[i])

        # op = 1, we have a REQUEST
        else:

            # some output to tell us what is going on
            print "%s: REQUEST tag %s" % (now(), tag[i])

            # let the request transaction happen
            yield h.request(tag[i], int(ts[i]/2))

            # transaction is finished
            print "%s REQUEST fulfilled, got %s" % (now(), h.item)


def main():
    """ Main function """
    # instance of users, give them an instance of the wireless hub
    u = users(h)

    # return local generator for simulation
    return u

# using MyHDL simulation environment, give it main
sim = Simulation(main())

# run simulation
sim.run()
