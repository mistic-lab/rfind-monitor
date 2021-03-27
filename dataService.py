import numpy as np
import h5py

def rebin(arr, NFFT, length):

    n = int(np.ceil(NFFT/length)) # number to average together until the end
    nearest_size_down = int(np.floor(NFFT/n))
    out = np.empty((length))
    out[:nearest_size_down] = arr[:nearest_size_down*n].reshape(-1,n).mean(axis=1)
    out[nearest_size_down:] = arr[nearest_size_down*n:].mean()

    return out

def fetch_integration(int, h5FileHandle, start, end, length):
    """
    Fetches an integration from an h5 file and returns it to dash.

    :Parameters:
    - int: integer integration number to fetch (translates to index in h5)
    - h5FileHandle: and already open h5 file handle so I don't have to open and close it every integration
    - start: start index to fetch in frequency
    - end: end index to fetch in frequency
    - length: how many samples should I return?
    """
    fs = h5FileHandle.attrs['fs']
    NFFT = h5FileHandle.attrs['NFFT']

    spec = np.array(h5FileHandle['spec'][int][start:end])
    freqs = np.array(h5FileHandle['freqs'][start:end])

    if len(spec) > length:
        spec = rebin(spec, NFFT, length)
        freqs = rebin(freqs, NFFT, length)

    t = h5FileHandle['times'][int]

    return spec, freqs, t, fs, NFFT