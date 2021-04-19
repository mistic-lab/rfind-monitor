import numpy as np

NBINS = 600000

FS = 2e9

SPEC_WIDTH = 1000

WATERFALL_HEIGHT = 120

FULL_FREQS = np.linspace(0, FS, NBINS)
FULL_FREQS.setflags(write=False)

PLASMA_SOCKET='/home/ubuntu/plasma'#'/tmp/plasma'
ZMQ_ADDR = 'tcp://*:5557'

