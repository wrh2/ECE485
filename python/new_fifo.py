"""
  High level modeling of First In First Out cache
  for ECE485 final project
  Programmed by William Harrington
"""
from myhdl import *
from random import randrange

def trigger(event):
    """
    Function for triggering events

    :param input event: event to trigger
    """
    event.next = not event

class fifo:
    """
    Class definition for First In, First Out high level cache model
    """

    def __init__(self):
        """
        Class initialization

        :class member mem: memory
        :class member tags: tags associated with memory
        :class member sync: synchronization signal
        :class member evict: last evicted item
        :class member capacity: capacity of memory
        :class member hit: tag present signal
        """
        self.mem = []
        self.tags = []
        self.sync = Signal(0)
        self.evict = None
        self.capacity = 16
        self.hit = Signal(0)
        self.data_out = 0
        self.valid = 0

    def write(self, data, tag):
        """
        Writie method

        :param input self: class object
        :param input data: data to write
        :param input tag: tag to write to
        """
        # non time-consuming method

        # check if tag is present
        try:
            val = self.tags.index(tag)

        # make an exception if value isn't there
        except ValueError:

            # miss
            self.hit.next = 0

            # check to see if memory is at capacity
            if len(self.mem) >= self.capacity:
                # need to perform eviction
                self.evict = self.mem.pop()

            # write to beginning of list
            self.mem.insert(0, data)
            self.tags.insert(0, tag)

            # trigger event
            trigger(self.sync)

        # no exception
        else:

            # hit, tag was present
            self.hit.next = 1

            # write data to index in memory
            self.mem[val] = data

            # trigger event
            trigger(self.sync)

    def read(self, tag):
        """
        Read method

        :param input self: instance
        :param input tag: tag to read
        """
        # time-consuming method

        # check for empty memory
        if not self.mem:

            # read empty memory, definitely a miss
            self.hit.next = 0

            # resume when event is triggered
            yield self.sync

        else:

            # check for tag in memory
            try:
                val = self.tags.index(tag)

            # make an exception if the value isn't there
            except ValueError:

                # big ol miss
                self.hit.next = 0

                # no data or tag to return
                self.data_out = 0
                self.valid = 0

                yield self.sync

            else:

                # got something
                self.hit.next = 1

                # return data
                self.data_out = self.mem[val]
                
                # return tag
                self.valid = self.tags[val]

                yield self.sync

# instance of fifo memory
f = fifo()

def write_op(f):
    """
    Write operation

    :param input f: fifo instance
    """
    yield delay(150) # 15 clk cycle delay

    # generate 5 random transaction sizes
    for i in range(5):

        # random transaction size, 0-1024 in steps of 128
        # this makes the number that is returned always divisible
        # by 128
        rand_ts = randrange(0, 1024, 128)

        # randrom tag from 0 to 15
        rand_tag = randrange(0, 15, 1)

        # write to fifo memory
        f.write(rand_ts, rand_tag)

        # output
        if f.hit:
            print "%s: wrote %s bytes to tag %s, HIT" % (now(), rand_ts, rand_tag)
        # gotta write to data center
        else:
            print "%s: wrote %s bytes to tag %s, MISS contacting data center" % (now(), rand_ts, rand_tag)
            yield delay(1500)

def read_op(f):
    """
    Read operation

    :param input
    """
    yield delay(150) # 15 clk cycle delay

    # try to read memory
    while True:
        # announce accessing of memory
        print "%s: trying to read memory" % now()

        # get read result
        yield f.read(randrange(0, 15,1))

        # if we got a hit
        if f.hit:
            # output message is this
            print "%s: read %s bytes, tag was %s, HIT" % (now(), f.data_out, f.valid)

        # miss
        else:
            # output message is this
            print "%s: reads %s bytes, MISS, contacting data center" % (now(), f.data_out)
            yield delay(1500) # additional latency for data center access

def main():
    W = write_op(f)
    R = read_op(f)
    return W, R

sim = Simulation(main())
sim.run()
