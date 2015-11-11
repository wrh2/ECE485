"""
  First in first out example from MyHDL documentation
  Code is slighty modified and has a testbench
  Programmed by William Harrington
  ECE485 HW4
"""
from myhdl import *
from random import randrange
import sys

def fifo(re, we, addr, hit, dout, din, clk, maxFilling=16):
    """
    2-way set associative cache with first in first out replacement policy

    :param input re:            read enable
    :param input we:            write enable
    :param input index:         index, cache line to select in the cache
    :param input tag:           tag for cache line
    :param input din:           data to write to the cache
    :param input clk:           clock

    :param output hit:          hit/miss
    :param output dout:         data output

    :param optional maxFilling: number of lines in a cache set
    """

    # set up the lines for the cache
    #cache_line = {'valid': Signal(intbv(0)), 'tag': Signal(intbv(randrange(2**11))[11:]), 'data': Signal(intbv(0)[8:])}
    cache_line = Signal(intbv(0, min=0, max=(2**20-1)))

    # create list of 16 cache lines
    cache_set = [cache_line for k in range(maxFilling)]

    # create a cache with 2 sets
    cache = [cache_set for i in range(2)]

    # first in first out cache replacement policy
    @always(clk.posedge)
    def access():

        # split up address bits

        # 11 bits for the tag
        tag = addr[15:5]

        # 4 bits for the index
        #index = addr[4:1]

        # one bit for byte select
        #bs = addr[0]

        # write operation
        if we and not re:

            # go through both sets in the cache
            for n in range(len(cache)):

                # pop off oldest cache line
                cache[n].pop()

                # insert a new cache line in the beginning
                cache[n].insert(0, cache_line)

                # set the valid bit on the new cache line
                cache[n][0].next[19] = not cache[n][0][19]

                # generate a tag for the cache line, random 11 bit value
                cache[n][0].next[18:9] = intbv(randrange(2**9))

                # set the data in the cache line
                cache[n][0].next[8:] = din

        # read operation
        elif ((re and not we)):

            # go through both sets in the cache
            for n in range(len(cache)):

                # go through the lines in the set
                for m in range(len(cache[n])):

                    # compare tag bits and check valid bit
                    if cache[n][m][18:9] == tag and cache[n][m][19]:

                        # we got something
                        hit = 1

                        # output the data
                        dout.next = cache[n][m][8:]

                    # tag bits didn't match or valid bit wasn't set
                    else:

                        # you get nothing! good day sir!
                        hit = 0
                        dout.next = 0

        # wait until read or write operation happens
        else:
            hit = 0
            dout.next = 0

    # return local generator
    return access

def testbench():
    """
    Test bench for cacheFSM
    """

    # initialize signals
    r, w, hit, clk = [Signal(bool(0)) for i in range(4)]
    addr = Signal(intbv(0, min=0, max=2**16))
    dout, din = [Signal(intbv(0, min=0, max=2**8)) for i in range(2)]

    # instance of fifo cache
    fifo_inst = fifo(r, w, addr, hit, dout, din, clk)

    # clock generation
    @always(delay(10))
    def clkgen():
        clk.next = not clk

    # randomly change inputs to FSM
    @always(clk.posedge)
    def stimulus():
        # generate next address signal
        addr.next = intbv(randrange(2**16), min=0, max=2**16)

        # generate next read signal
        r.next = bool(randrange(2))

        # generate next write signal
        w.next = bool(randrange(2))

        # if next write signal is high
        if w.next:

            # generate next data signal
            din.next = intbv(randrange(256), min=0, max=2**8)

        else:
            din.next = intbv(0, min=0, max=2**8)

    # print the output, just for fun
    @instance
    def output_monitor():
        print "dout din r w hit clk"
        print "--------------------"
        while True:
            yield clk.posedge
            yield delay(1)
            print "%d %d %d %d %d" % (dout, din, r, w, hit),
            yield clk.posedge
            print "C"#,
            #yield delay(1)
            #print state

    return fifo_inst, clkgen, output_monitor, stimulus


def simulate(timesteps):
    """
    Function simulates test bench

    :param timesteps: number of timesteps, integer
    """
    tb = traceSignals(testbench)
    #tb = testbench()
    sim = Simulation(tb)
    sim.run(timesteps)

# call simulate function to simulate!
simulate(2000)
