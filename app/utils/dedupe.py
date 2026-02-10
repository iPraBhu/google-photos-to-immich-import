import hashlib
from typing import BinaryIO

def sha256_stream(fileobj: BinaryIO, chunk_size: int = 8192) -> str:
    h = hashlib.sha256()
    while True:
        chunk = fileobj.read(chunk_size)
        if not chunk:
            break
        h.update(chunk)
    return h.hexdigest()
