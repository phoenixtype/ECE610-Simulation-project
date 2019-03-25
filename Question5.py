""" A queue example with GI inter-arrival times and exponential service times.

    For more information and formulas for moments see: https://en.wikipedia.org/wiki/Weibull_distribution

    Since we are using a GI distribution for arrival times we cannot assume the PASTA principle (Poisson
    arrivals See Time Averages) hence we set up a separate queue monitoring process to watch how the
    packet queue size varies over time and to compute the average queue size.
"""
import random
import simpy
import math
import matplotlib.pyplot as plt


class Packet(object):
    """ A very simple class that represents a packet.
        This packet will run through a queue at a switch output port.

        Parameters
        ----------
        time : float
            the time the packet arrives at the output queue.
        id : int
            an identifier for the packet (not used for anything yet)
        src, dst : int
            identifiers for source and destination (not used yet)
    """

    def __init__(self, time, id, src="a", dst="z"):
        self.time = time
        self.id = id
        self.src = src
        self.dst = dst


def packet_generator(env, out_pipe):
    """ A generator function for endlessly creating packets.
        Generates packets with exponentially varying inter-arrival times and
        placing them in an output queue.

        Parameters
        ----------
        env : simpy.Environment
            The simulation environment.
        out_pipe : simpy.Store
            the output queue model object.
    """
    global packets_sent
    while True:
        # wait for next transmission
        yield env.timeout(random.weibullvariate(WSCALE, SHAPE))
        # yield env.timeout(random.expovariate(1.0/ARRIVAL))
        # print "Sending packet {} at time {}".format(i, env.now)
        packets_sent += 1
        p = Packet(env.now, packets_sent)
        yield out_pipe.put(p)


def packet_consumer(env, in_pipe):
    """ A generator function which consumes packets.
        Consumes packets from the packet queue, i.e., models sending a packet of exponentially
        varying size over a link.

        Parameters
        ----------
        env : simpy.Environment
            the simulation environment.
        in_pipe : simpy.Store
            the FIFO model object where packets are kept.
    """
    global queue_wait, total_wait

    while True:
        # Get event for message pipe
        msg = yield in_pipe.get()
        queue_wait += env.now - msg.time
        yield env.timeout(random.expovariate(1 / SERVICE))
        total_wait += env.now - msg.time
        # print "at time {} processed packet: {} ".format(env.now, msg.id)


def queue_monitor(env, out_pipe):
    """ A generator function for monitoring a packet queue.

        Parameters
        ----------
        env : simpy.Environment
            the simulation environment.
        out_pipe : simpy.Store
            the FIFO model object whose queue is to be monitored.
    """
    global queue_size, queue_occupancy
    while True:
        yield env.timeout(1.0)
        queue_size += len(out_pipe.items)
        queue_occupancy.append(len(out_pipe.items))
        # print "Time = {}".format(env.now)


if __name__ == '__main__':
    SHAPE = 2
    ARRIVAL = 5
    SERVICE = 4
    # The G1 scale parameter computed based on the shape and average inter-arrival time.
    WSCALE = ARRIVAL / math.gamma(1.0 + 1.0 / SHAPE)

    queue_wait = 0
    total_wait = 0
    queue_size = 0
    packets_sent = 0
    queue_occupancy = []

    # Setup and start the simulation
    env = simpy.Environment()
    pipe = simpy.Store(env)
    env.process(queue_monitor(env, pipe))
    env.process(packet_generator(env, pipe))
    env.process(packet_consumer(env, pipe))
    print('A GI/M/1 queueing simulation')
    env.run(until=1.0e5)

    print("Ending simulation time: {}".format(env.now))
    print("Packets sent: {}".format(packets_sent))
    # Formulas from Klienrock, "Queueing Systems, Volume I:Theory", 1975.
    mu = 1.0 / SERVICE
    l = 1.0 / ARRIVAL
    rho = l / mu
    W = rho / mu / (1 - rho)  # average weight in the queue
    T = 1 / mu / (1 - rho)  # average total system time.
    nq_bar = rho / (1.0 - rho) - rho  # The average number waiting in the queue
    print("M/M/1 Theory: avg queue wait {}, avg total time {}, avg queue size {}".format(W, T, nq_bar))
    print('Sim Average queue wait = {}'.format(queue_wait / packets_sent))
    print('Sim Average total wait = {}'.format(total_wait / packets_sent))
    print('Sim Average queue size = {}'.format(queue_size / env.now))
    fig, axis = plt.subplots()
    axis.hist(queue_occupancy, bins=100, density=True)
    axis.set_title(r"Histogram of a GI process output queue")
    axis.set_xlabel("x")
    axis.set_ylabel("normalized frequency of occurrence")
    axis.set_xlim([0, 25])
    # fig.savefig("GIQueueHistogram.png")
    plt.show()
