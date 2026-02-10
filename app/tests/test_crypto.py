from app.utils.crypto import encrypt_secret, decrypt_secret

def test_encrypt_decrypt():
    secret = "mysecret"
    token = encrypt_secret(secret)
    assert decrypt_secret(token) == secret
