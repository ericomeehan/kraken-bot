import numpy
from scipy import stats

def linear_regression(timestamps, values):
    x = numpy.array(timestamps)
    y = numpy.array(values)
    
    return stats.linregress(x, y)
