import zmq
import zlib
from brain_plasma import Brain
import pickle
import numpy as np
import const

# SRC is NRC zmq connection, server_brain is in CC cloud VM memory

def middleman(rate):
    context_SRC = zmq.Context()
    zmq_socket_SRC = context_SRC.socket(zmq.PULL)
    zmq_socket_SRC.bind(const.ZMQ_ADDR)

    poller = zmq.Poller()
    poller.register(zmq_socket_SRC, zmq.POLLIN)

    server_brain = Brain(path=const.PLASMA_SOCKET)


    i=1
    while True:
        print(f"Iteration {i}")
        socks = dict(poller.poll(rate))
        if socks:
            print("- Pulling from SRC")
            msg = zmq_socket_SRC.recv(zmq.NOBLOCK)
            print("-- Successfully pulled")
            print("- Trying to publish to WEB")
            try:
                p = zlib.decompress(msg)
                data = pickle.loads(p)
                server_brain['spec'] = np.array(data[:-1])
                server_brain['timestamp'] = data[-1]

                print("-- Successfully added to brain")
            except zmq.error.Again:
                print("-- Failed to publish")
                pass
        else:
            print("-- Failed to pull")
            pass
        
        i+=1

middleman(400)

