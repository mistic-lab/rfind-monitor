import zmq

# SRC is NRC, WEB is CC cloud
# def middleman(rate):
#     """
#     rate is in ms
#     """
#     context_SRC = zmq.Context()
#     zmq_socket_SRC = context_SRC.socket(zmq.PULL)
#     zmq_socket_SRC.bind("tcp://*:5557")

#     poller = zmq.Poller()
#     poller.register(zmq_socket_SRC, zmq.POLLIN)

#     context_WEB = zmq.Context()
#     zmq_socket_WEB = context_WEB.socket(zmq.PUB)
#     zmq_socket_WEB.bind("tcp://127.0.0.1:5558")

#     i=1
#     while True:
#         socks = dict(poller.poll(rate))
#         if socks:
#             msg = zmq_socket_SRC.recv(zmq.NOBLOCK)
#             try:
#                 zmq_socket_WEB.send(msg, zmq.NOBLOCK)
#             except:
#                 pass
#         i+=1

## Verbose
def middleman(rate):
    context_SRC = zmq.Context()
    zmq_socket_SRC = context_SRC.socket(zmq.PULL)
    zmq_socket_SRC.bind("tcp://*:5557")

    poller = zmq.Poller()
    poller.register(zmq_socket_SRC, zmq.POLLIN)

    context_WEB = zmq.Context()
    zmq_socket_WEB = context_WEB.socket(zmq.PUB)
    zmq_socket_WEB.bind("tcp://127.0.0.1:5558")

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
                zmq_socket_WEB.send(msg)#, zmq.NOBLOCK)
                print("-- Successfully published")
            except zmq.error.Again:
                print("-- Failed to publish")
        else:
            print("-- Failed to pull")
        
        i+=1

middleman(400)

