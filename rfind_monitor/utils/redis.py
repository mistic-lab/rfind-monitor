import msgpack
import msgpack_numpy as m
import numpy as np
import redis
m.patch()

def numpy_to_Redis(redis_client,array,key):
    """Store given Numpy array 'array' in Redis under key 'key'"""
    packed_arr = m.packb(array)
    redis_client.set(key,packed_arr)
    return

def numpy_from_Redis(redis_client,key)->np.array:
    """Retrieve Numpy array from Redis key 'key'"""
    packed_arr = redis_client.get(key)
    array = m.unpackb(redis_client.get(key))
    return array

