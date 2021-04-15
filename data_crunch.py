import numpy as np

import const

def bisection(array,value):
    '''Given an ``array`` , and given a ``value`` , returns an index j such that ``value`` is between array[j]
    and array[j+1]. ``array`` must be monotonic increasing. j=-1 or j=len(array) is returned
    to indicate that ``value`` is out of range below and above respectively.'''
    n = len(array)
    if (value < array[0]):
        return -1
    elif (value > array[n-1]):
        return n
    jl = 0# Initialize lower
    ju = n-1# and upper limits.
    while (ju-jl > 1):# If we are not yet done,
        jm=(ju+jl) >> 1# compute a midpoint with a bitshift
        if (value >= array[jm]):
            jl=jm# and replace either the lower limit
        else:
            ju=jm# or the upper limit, as appropriate.
        # Repeat until the test condition is satisfied.
    if (value == array[0]):# edge cases at bottom
        return 0
    elif (value == array[n-1]):# and top
        return n-1
    else:
        return jl


def fetch_integration(integration, h5FileHandle, f1, f2, length):
    """
    Fetches an integration from an h5 file and returns it to dash.

    :Parameters:
    - int: integer integration number to fetch (translates to index in h5)
    - h5FileHandle: and already open h5 file handle so I don't have to open and close it every integration
    - f1: start frequency (Hz)
    - f2: end frequency (Hz)
    - length: how many samples should I return?
    """
    allFreqs = np.array(h5FileHandle['freqs'])
    index1 = bisection(allFreqs, f1)
    index2 = bisection(allFreqs, f2)-1

    requested_len = index2-index1+1
    num_to_bin = int(np.ceil(requested_len/length))
    even_divisor = int(np.floor(requested_len/num_to_bin))
    new_length = num_to_bin*even_divisor

    index2 = int(index1+new_length)

    freqs = np.linspace(allFreqs[index1],allFreqs[index2-1],length)
    spec = np.empty(length)

    waterfall_len = h5FileHandle['spec'].shape[0]

    start = np.array(h5FileHandle['spec'][integration % waterfall_len][index1:index2])

    spec[:even_divisor] = start.reshape(-1,num_to_bin).max(axis=1)
    spec[even_divisor:] = start[-1]

    timestamp = h5FileHandle['times'][integration % waterfall_len]

    return spec, freqs, timestamp


def reduce_integration(integration, f1, f2, nbins):

    index1 = bisection(const.FULL_FREQS, f1)
    index2 = bisection(const.FULL_FREQS, f2)-1


    requested_len = index2-index1+1
    num_to_bin = int(np.ceil(requested_len/nbins))
    even_divisor = int(np.floor(requested_len/num_to_bin))
    new_length = num_to_bin*even_divisor

    index2 = int(index1+new_length)

    current_freqs = np.linspace(const.FULL_FREQS[index1], const.FULL_FREQS[index2-1], nbins)
    reduced_integration = np.empty(nbins)

    
    integration = integration[index1:index2]
    reduced_integration[:even_divisor] = integration.reshape(-1,num_to_bin).max(axis=1)
    reduced_integration[even_divisor:] = integration[-1]

    return reduced_integration, current_freqs

