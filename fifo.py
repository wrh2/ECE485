"""
  First in first out example from MyHDL documentation
  Code is slighty modified and has a testbench
  Programmed by William Harrington
  ECE485 HW4
"""
from myhdl import *
from random import randrange
import sys

def fifo(re, we, addr, hit, valid, dout, din, clk, maxFilling=16):
    """
    2-way set associative cache with first in first out replacement policy

    :param input re:            read enable
    :param input we:            write enable
    :param input addr:          address to read/write from
    :param input din:           data to write to the cache
    :param input clk:           clock

    :param output hit:          hit/miss
    :param output dout:         data output

    :param optional maxFilling: number of lines in a cache set
    """

    # set up the lines for the cache
    cache_line = {'valid': Signal(intbv(0)), 'tag': Signal(intbv(randrange(2**11))[11:]), 'data': Signal(intbv(0)[8:])}
    
    # create list of 16 cache lines
    cache_set = [cache_line for k in range(maxFilling)]

    # create a cache with 2 sets
    cache = [cache_set for i in range(2)]

    # first in first out cache replacement policy
    @always(clk.posedge)
    def access():
        """
        Function describes the behavior of a cache access
        """

        # split up address bits

        # 11 bits for the tag
        tag = addr[16:5]

        # 4 bits for the index
        index_bits = addr[4:1]
        index = int(addr[4:1])

        # one bit for byte select
        bs = int(addr[0])

        # write operation
        if we and not re:

            # check for hit
            if ((cache[bs][index]['tag'] == tag) and (cache[bs][index]['valid'])):
                hit.next = 1 # write hit
                cache[bs][index]['data'].next = din
            else:
                hit.next = 0 # write miss

                # first in, first out behavior below

                # pop off oldest item
                cache[bs].pop()

                # place at beginning
                cache[bs].insert(0, cache_line)

                # set valid bit
                cache[bs][0]['valid'].next = 1

                # set tag
                cache[bs][0]['tag'].next = tag

                # write data
                cache[bs][0]['data'].next = din

            # keep track of last valid address, so our simulation can do some interesting stuff
            valid.next = addr

        # read operation
        elif ((re and not we)):

            # check for tag and valid bits
            if cache[bs][index]['tag'] == tag and cache[bs][index]['valid']:

                # read hit
                hit.next = 1
                dout.next = cache[bs][index]['data']
            else:
                # read miss
                hit.next = 0
                dout.next = 0

        # wait until read or write operation happens
        else:
            hit.next = 0
            dout.next = 0

    # return local generator
    return access

def fifo_bench():
    """
    Test bench for fifo cache
    """

    # initialize signals
    r, w, hit, clk = [Signal(bool(0)) for i in range(4)]
    addr = Signal(intbv(0, min=0, max=2**16))
    valid = Signal(intbv(0, min=0, max=2**16))
    dout, din = [Signal(intbv(0, min=0, max=2**8)) for i in range(2)]

    # instance of fifo cache
    fifo_inst = fifo(r, w, addr, hit, valid, dout, din, clk)
    #fifo_inst = toVerilog(fifo, r, w, addr, hit, valid, dout, din, clk)

    # clock generation
    @always(delay(10))
    def clkgen():
        clk.next = not clk

    # randomly change inputs to FSM
    @always(clk.posedge)
    def stimulus():

        if valid.next:
            addr.next = valid.next
        else:
            # generate next address signal
            addr.next = intbv(randrange(2**16), min=0, max=2**16)

        # generate next read signal
        r.next = bool(randrange(2))

        # generate next write signal
        w.next = bool(randrange(2))

        # if next write signal is high and read is low
        if (w.next and (not r.next)):

            # generate next data signal
            din.next = intbv(randrange(256), min=0, max=2**8)

        # otherwise
        else:

            # din.next will be low
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
    tb = traceSignals(fifo_bench)
    #tb = fifo_bench()
    sim = Simulation(tb)
    sim.run(timesteps)

# call simulate function to simulate!
simulate(2000)
