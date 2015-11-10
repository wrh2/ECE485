"""
  Very simple state machine for cache
  Programmed by William Harrington
  ECE485 HW4
"""
from myhdl import *
from random import randrange

# declare states
t_State = enum('WAIT', 'READ', 'WRITE')

def cacheFSM(addr, r, w, din, dout, clk, state):
    """
    Function contains finite state machine definition

    :param r:     input read
    :param w:     input write
    :param clk:   clock
    :param state: current state
    """

    # not sure what intbv really is or why the [8:] is necessary
    #mem = [Signal(0)[8:]) for i in range(128)]

    # lets try this, assign random ints to memory just to fill it up
    # data bus width is 8 bits so nothing over 255
    # and lets make the memory have 256 slots because I'm just testing right now
    mem = [Signal(randrange(255)) for i in range(256)]

    @always(clk.posedge)
    def logic():

        # read is high, write is low
        if r == 1 and w == 0:

            # next state is read
            state.next = t_State.READ
            dout.next = mem[addr]

        # write is high, read is low
        elif w == 1 and r == 0:

            # next state is write
            state.next = t_State.WRITE
            mem[addr].next = din

        # both high or both low
        else:

            # next state is wait
            state.next = t_State.WAIT

    # return local generator
    return logic

def testbench():
    """
    Test bench for cacheFSM
    """

    # initialize signals
    r, w, clk = [Signal(bool(0)) for i in range(3)]
    dout = Signal(0)
    addr = Signal(0)
    din = Signal(0)
    state = Signal(t_State.WAIT) # default state

    # instance of cacheFSM
    #cache_inst = cacheFSM(addr, r, w, din, dout, clk, state)
    cache_inst = toVerilog(cacheFSM, addr, r, w, din, dout, clk, state)

    # clock generation
    @always(delay(10))
    def clkgen():
        clk.next = not clk

    # randomly change inputs to FSM
    @always(clk.posedge)
    def stimulus():
        r.next = randrange(2)
        w.next = randrange(2)
        addr.next = randrange(255)
        din.next = randrange(255)

    # print the output, just for fun
    @instance
    def output_monitor():
        print "r w addr din dout clk state"
        print "---------------------------"
        while True:
            yield clk.posedge
            yield delay(1)
            print "%d %d %d %d %d" % (r, w, addr, din, dout),
            yield clk.posedge
            print "C",
            yield delay(1)
            print state

    return cache_inst, clkgen, output_monitor, stimulus


def simulate(timesteps):
    """
    Function simulates test bench

    :param timesteps: number of timesteps, integer
    """
    #tb = traceSignals(testbench)
    tb = testbench()
    sim = Simulation(tb)
    sim.run(timesteps)

# call simulate function to simulate!
simulate(2000)
