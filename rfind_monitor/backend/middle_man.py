import time
import zmq
import numpy as np
import redis
import msgpack
import msgpack_numpy as m
import redis
m.patch()

import rfind_monitor.const as const
from rfind_monitor.utils.redis import numpy_to_Redis




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
            tic = time.time()
            msg = zmq_socket_SRC.recv(zmq.NOBLOCK)
            toc = time.time()
            print(f"Time to receive from zmq: {toc-tic}")
            try:
                tic = time.time()
                redis_client.set('latest', msg)
                toc = time.time()
                print(f"Time to set to redis: {toc-tic}")
                if verbose: print(f"Passed data from zmq to redis {i}")


            except Exception as e:
                if verbose: print(f"-- Failed to send {e}")
                pass
        else:
            pass
        
        i+=1

if __name__ == "__main__":
    middleman(const.MIDDLE_MAN_RATE, verbose=True)

