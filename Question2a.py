# Copyright 2014 Dr. Greg M. Bernstein
""" A simple script that uses the Python *random* library and the *matplotlib*
    library to create histogram of exponentially distributed random numbers.
"""

import random
import  math
import matplotlib.pyplot as plt

if __name__ == '__main__':
    # Generate a list of samples
    # This technique is called a "list comprehension" in Python
    expSamples = [random.expovariate(0.2) for i in range(10000)]
    print(expSamples[0:10])  #Take a look at the first 10
    fig, axis = plt.subplots()
    axis.hist(expSamples, bins=100, density=True, log=True)
    axis.set_title(r"Histogram of an exponential RNG $\lambda = 1/5$")
    axis.set_xlabel("x")
    axis.set_ylabel("normalized frequency of occurrence")
    fig.savefig("ExponentialHistogram.png")
    plt.show()
