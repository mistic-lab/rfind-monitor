import numpy as np
import h5py

def fetch_integration(int, h5FileHandle):
    fs = h5FileHandle.attrs['fs']
    NFFT = h5FileHandle.attrs['NFFT']
    
    spec = h5FileHandle['spec'][int]
    freqs = h5FileHandle['freqs']
    t = h5FileHandle['times'][int]

    return spec, freqs, t, fs, NFFT