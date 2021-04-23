import numpy as np

NBINS = 600000
FS = 2e9

FULL_FREQS = np.linspace(0, FS, NBINS)
FULL_FREQS.setflags(write=False)

DTYPE = np.int8