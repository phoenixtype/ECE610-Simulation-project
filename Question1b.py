import numpy as np
import matplotlib.pyplot as plt
from pylab import *

n = 10000
bin_count = 100
data = [np.random.random() for i in range(n)]
values, base = np.histogram(data, bins=bin_count)
values = [float(j)/n for j in values]
cumulative = np.cumsum(values)
cumulative2 = [1-i for i in cumulative]
test = [cumulative2[i] for i in range(41,61)]
xaxis = [float(i)/bin_count for i in range(41,61)]
plot(xaxis, test)
plt.show()
