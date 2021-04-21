from pyarrow import plasma
from typing import ByteString
import hashlib

def name_to_hash(name: str) -> plasma.ObjectID:
    """
    hash the name to 20 bytes
    create a plasma.ObjectId
    """
    name_hash = _hash(name, 20)
    _id = plasma.ObjectID(name_hash)
    return _id

def _hash(name: str, digest_bytes: int) -> ByteString:
        """
        input a name str
        return a bytestring with length hex_bytes of the name string
        """
        return hashlib.blake2b(name.encode(), digest_size=digest_bytes).digest()