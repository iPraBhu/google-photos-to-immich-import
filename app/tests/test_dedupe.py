import io
from app.utils.dedupe import sha256_stream

def test_sha256_stream():
    data = b"hello world"
    f = io.BytesIO(data)
    assert sha256_stream(f) == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
