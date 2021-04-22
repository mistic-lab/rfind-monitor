import numpy as np
import h5py
import time
import msgpack_numpy as m
m.patch()
# import redis
import zmq

import rfind_monitor.const as const

ZMQ_IP_PUSH = '127.0.0.1'
SOURCE_H5 = '/home/ubuntu/rfind-monitor/data.h5'

def producer(verbose=False):

    pusher_addr = const.ZMQ_PROTOCOL+"://"+ZMQ_IP_PUSH+":"+const.ZMQ_PORT

    context = zmq.Context()
    zmq_socket = context.socket(zmq.PUSH)
    zmq_socket.connect(pusher_addr)

    # redis_client = redis.Redis(host=const.REDIS_REMOTE_IP, port=const.REDIS_PORT, db=0, password=const.REDIS_REMOTE_PASSWORD, username=const.REDIS_REMOTE_USER)

    with h5py.File(const.SOURCE_H5,'r') as h5f:
        if verbose: print(f"Using {SOURCE_H5} as file source")

        modlen = len(h5f['times'])

        i=0
        while True:
            if verbose: print(f"Trying to send iteration {i} to redis store")
            spec = np.array(h5f['spec'][i % modlen]).tolist()
            timestamp = h5f['times'][i % modlen]
            spec.append(timestamp)
            msg = m.packb(spec)
            try:
                # redis_client.set('latest',msg)
                zmq_socket.send(msg, zmq.NOBLOCK)
                if verbose: print("-- Succeeded")
            except Exception as e:
                if verbose: print(f"-- Failed: {e}")
            time.sleep(const.INTEGRATION_RATE/1000)
            i+=1


producer(verbose=True)

