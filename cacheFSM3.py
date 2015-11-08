"""
  Very simple state machine for cache
  Programmed by William Harrington
  ECE485 HW4
"""
from myhdl import *
from random import randrange

# declare states
t_State = enum('WAIT', 'READ', 'WRITE')

def cacheFSM(r, w, clk, state):
    """
    Function contains finite state machine definition

    :param r:     input read
    :param w:     input write
    :param clk:   clock
    :param state: current state
    """

    @always(clk.posedge)
    def logic():

        # read is high, write is low
        if r == 1 and w == 0:

            # next state is read
            state.next = t_State.READ

        # write is high, read is low
        elif w == 1 and r == 0:

            # next state is write
            state.next = t_State.WRITE

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
    state = Signal(t_State.WAIT) # default state

    # instance of cacheFSM
    cache_inst = cacheFSM(r, w, clk, state)

    # clock generation
    @always(delay(10))
    def clkgen():
        clk.next = not clk

    # randomly change inputs to FSM
    @always(clk.posedge)
    def stimulus():
        r.next = randrange(2)
        w.next = randrange(2)


    # print the output, just for fun
    @instance
    def output_monitor():
        print "r w clk state"
        print "-------------"
        while True:
            yield clk.posedge
            yield delay(1)
            print "%d %d" % (r, w),
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
    tb = traceSignals(testbench)
    sim = Simulation(tb)
    sim.run(timesteps)

# call simulate function to simulate!
simulate(2000)
