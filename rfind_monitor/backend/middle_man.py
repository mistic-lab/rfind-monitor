import zmq
import zlib
from brain_plasma import Brain
import pickle
import numpy as np

import rfind_monitor.const as const

# SRC is NRC zmq connection, server_brain is in CC cloud VM memory

def middleman(rate, verbose=False):
    context_SRC = zmq.Context()
    zmq_socket_SRC = context_SRC.socket(zmq.PULL)
    zmq_socket_SRC.bind(const.ZMQ_ADDR)

    poller = zmq.Poller()
    poller.register(zmq_socket_SRC, zmq.POLLIN)

    server_brain = Brain(path=const.PLASMA_SOCKET)


    i=1
    while True:
        if verbose: print(f"Iteration {i}")
        socks = dict(poller.poll(rate))
        if socks:
            if verbose: print("- Pulling from SRC")
            msg = zmq_socket_SRC.recv(zmq.NOBLOCK)
            if verbose: print("-- Successfully pulled")
            if verbose: print("- Trying to publish to WEB")
            try:
                p = zlib.decompress(msg)
                data = pickle.loads(p)
                server_brain['spec'] = np.array(data[:-1])
                server_brain['timestamp'] = data[-1]

                if verbose: print("-- Successfully added to brain")

            except zmq.error.Again:
                if verbose: print("-- Failed to publish")
                pass
        else:
            if verbose: print("-- Failed to pull")
            pass
        
        i+=1

if __name__ == "__main__":
    middleman(400, verbose=True)

