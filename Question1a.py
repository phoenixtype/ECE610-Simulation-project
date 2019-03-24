import numpy as np
import random
from pylab import *

n = 10000
bin_count = 100
data = [np.random.random() for i in range(n)]
values, base = np.histogram(data, bins=bin_count)
values = [float(j)/n for j in values]
cumulative = np.cumsum(values)
cumulative2 = [1-i for i in cumulative]
print(cumulative)
x_axis = [float(i) / bin_count for i in range(0, bin_count)]
plot(x_axis, cumulative)
plt.show()

