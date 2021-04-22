from pyarrow.plasma import start_plasma_store
import zmq
import zlib
import pickle
import numpy as np
import redis

import msgpack
import msgpack_numpy as m
import redis
m.patch()

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

    redis_client = redis.Redis(host=const.REDIS_IP, port=const.REDIS_PORT, db=0)




    i=1
    while True:
        socks = dict(poller.poll(rate))
        if socks:
            msg = zmq_socket_SRC.recv(zmq.NOBLOCK)
            try:
                redis_client.set('latest', msg)
                if verbose: print(f"Passed data from zmq to redis {i}")


            except Exception as e:
                if verbose: print(f"-- Failed to send {e}")
                pass
        else:
            pass
        
        i+=1

if __name__ == "__main__":
    middleman(const.MIDDLE_MAN_RATE, verbose=True)

