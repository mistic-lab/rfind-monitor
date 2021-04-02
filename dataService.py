import numpy as np

def rebin(arr, length):
    """
    len(arr) has to be at least length*2
    """

    out = np.empty((length))
        
    n = int(np.ceil(len(arr)/length)) # number to bin together until the boundary condition
    nearest_size_down = int(np.floor(len(arr)/n))

    out[:nearest_size_down] = arr[:nearest_size_down*n].reshape(-1,n).max(axis=1)
    out[nearest_size_down:] = arr[-1]

    return out

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
    fs = h5FileHandle.attrs['fs']
    NFFT = h5FileHandle.attrs['NFFT']

    allFreqs = np.array(h5FileHandle['freqs'])
    index1 = np.argmin([abs(f1-f) for f in allFreqs])
    index2 = np.argmin([abs(f2-f) for f in allFreqs])

    if (index2+1)-(index1+1) == length: #* The +1s handles the 0-999 case
        #* If it's already the correct length
        needsRebin = False
    elif ((index2+1)+(index1+1))/length < 2 or ((index2+1)-(index1+1) < length): 
        #* If it's not the correct length and it's too short to nicely rebin
        index1=int((index2+index1)/2 - length/2)
        index2 = int(index1+length)
        needsRebin = False
    else:
        needsRebin = True

    spec = np.array(h5FileHandle['spec'][integration][index1:index2])

    if needsRebin == True:
        spec = rebin(spec, length)

    freqs = np.linspace(allFreqs[index1],allFreqs[index2],length)

    t = h5FileHandle['times'][integration]

    return spec, freqs, t, fs, NFFT