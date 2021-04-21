import zmq
import numpy as np
import h5py
import time
import zlib
import pickle

import rfind_monitor.const as const

def producer(verbose=False):

    pusher_addr = const.ZMQ_PROTOCOL+"://"+const.ZMQ_IP_PUSH+":"+const.ZMQ_PORT

    const.SOURCE_H5

    context = zmq.Context()
    zmq_socket = context.socket(zmq.PUSH)
    zmq_socket.connect(pusher_addr)

    if verbose: print(f"Pushing to {pusher_addr}")

    with h5py.File(const.SOURCE_H5,'r') as h5f:
        if verbose: print(f"Using {const.SOURCE_H5} as file source")

        modlen = len(h5f['times'])

        i=0
        while True:
            if verbose: print(f"Trying to send iteration {i}")
            spec = np.array(h5f['spec'][i % modlen]).tolist()
            timestamp = h5f['times'][i % modlen]
            spec.append(timestamp)
            p = pickle.dumps(spec,protocol=-1)
            msg = zlib.compress(p)
            try:
                zmq_socket.send(msg, zmq.NOBLOCK)
                if verbose: print("-- Succeeded")
            except zmq.error.Again:
                if verbose: print("-- Failed")
            i+=1
            time.sleep(const.INTEGRATION_RATE/1000)


producer(verbose=True)

