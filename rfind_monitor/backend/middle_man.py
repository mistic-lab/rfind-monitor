from pyarrow.plasma import start_plasma_store
import zmq
import zlib
# from brain_plasma import Brain
# import pyarrow.plasma as plasma
# import pyarrow as pa
import pickle
import numpy as np
import redis

import rfind_monitor.const as const
from rfind_monitor.utils.hashing import name_to_hash
from rfind_monitor.utils.redis import numpy_to_Redis

# SRC is NRC zmq connection, server_brain is in CC cloud VM memory

def middleman(rate, verbose=False):
    context_SRC = zmq.Context()
    zmq_socket_SRC = context_SRC.socket(zmq.PULL)
    zmq_socket_SRC.bind(const.ZMQ_ADDR)

    poller = zmq.Poller()
    poller.register(zmq_socket_SRC, zmq.POLLIN)

    # server_brain = Brain(path=const.PLASMA_SOCKET)
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    # brain = plasma.connect(const.PLASMA_SOCKET)
    # spec_id = name_to_hash('spec')
    # timestamp_id = name_to_hash('timestamp')




    i=1
    while True:
        # if verbose: print(f"Iteration {i}")
        socks = dict(poller.poll(rate))
        if socks:
            # if verbose: print("- Pulling from SRC")
            msg = zmq_socket_SRC.recv(zmq.NOBLOCK)
            # if verbose: print("-- Successfully pulled")
            # if verbose: print("- Trying to publish to WEB")
            try:
                p = zlib.decompress(msg)
                data = pickle.loads(p)
                if verbose: print(f"Trying to write {data[-1]} to redis")
                numpy_to_Redis(redis_client, np.array(data[:-1]), 'spec')
                redis_client.set('timestamp',int(data[-1]))
                # server_brain['spec'] = pa.array(data[:-1])
                # server_brain['timestamp'] = data[-1]

                # if verbose: print(f" Brain contains {server_brain['timestamp']}\n")
                # spec_id = brain.put(data[:-1])
                # timestamp_id = brain.put(data[-1])
                # if verbose: print(f" Brain contains {brain.get(timestamp_id)}\n")

            except zmq.error.Again:
                # if verbose: print("-- Failed to publish")
                pass
        else:
            # if verbose: print("-- Failed to pull")
            pass
        
        i+=1

if __name__ == "__main__":
    middleman(const.MIDDLE_MAN_RATE, verbose=True)

