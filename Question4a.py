# Copyright 2014 Dr. Greg M. Bernstein
""" Simulation model for an M/Ek/1 queue based on SimPy. Estimates queue sizes and
    wait times and compares to theory.  Vary number of packets sent, inter-arrival
    and service time via parameters in the main portion of the script.

    Our model is based on processes for packet generation and consumption, along
    with a SimPy Store resource to model the FIFO output queue of a packet
    switching port.

    This code uses global (module) level variables and hence is not very extensible, nor
    an example of good OO design.
"""
import random
import simpy
import numpy as np
from scipy.stats import gamma


k = 1


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


def packet_generator(numPackets, env, out_pipe):
    """A generator function for creating packets.
         Generates packets with exponentially varying inter-arrival times and
         placing them in an output queue.

         Parameters
         ----------
        numPackets : int
            number of packets to send.
        env : simpy.Environment
            The simulation environment.
        out_pipe : simpy.Store
            the output queue model object.
    """
    global queue_size
    for i in range(numPackets):
        # wait for next transmission
        yield env.timeout(random.expovariate(1 / ARRIVAL))
        # print "Sending packet {} at time {}".format(i, env.now)
        p = Packet(env.now, i)
        # Measuring queue statistics here is only valid for Poisson arrivals.
        queue_size += len(out_pipe.items)
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
        yield env.timeout(random.expovariate(k / (SERVICE)))
        total_wait += env.now - msg.time
        # print "at time {} processed packet: {} ".format(env.now, msg.id)


if __name__ == '__main__':
    # The number of packets to be sent over the life of the simulation.
    NUM_PACKETS = 10000
    # The mean inter-arrival time
    ARRIVAL = 0.25
    # The mean service time
    SERVICE = 0.2

    # To compute the average queue waiting time
    queue_wait = 0
    # To compute the average total waiting time
    total_wait = 0
    # To compute the average queue size.
    queue_size = 0

    # Setup and start the simulation
    # The simulation environment.
    env = simpy.Environment()
    # The switch output port object based on the SimPy Store class
    pipe = simpy.Store(env)
    # Turns our generator functions into SimPy Processes
    env.process(packet_generator(NUM_PACKETS, env, pipe))
    env.process(packet_consumer(env, pipe))
    print('A simple M/Ek/1 queueing simulation')
    env.run()
    print("Ending simulation time: {}".format(env.now))
    # Formulas from Klienrock, "Queueing Systems, Volume I:Theory", 1975.
    mu = 1.0 / SERVICE
    l = 1.0 / ARRIVAL
    rho = l / mu
    W = rho / mu / (1 - rho)  # average wait in the queue
    T = 1 / mu / (1 - rho)  # average total system time.
    nq_bar = rho / (1.0 - rho) - rho  # The average number waiting in the queue
    print("Theory: avg queue wait (M/M/1) for comparison {}, avg total time {}, avg queue size {}".format(W, T, nq_bar))
    print('Sim Average queue wait = {}'.format(queue_wait / NUM_PACKETS))
    print('Sim Average total wait = {}'.format(total_wait / NUM_PACKETS))
    print('Sim Average queue size = {}'.format(queue_size / float(NUM_PACKETS)))
