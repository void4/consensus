from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.exceptions import InvalidSignature

chosen_hash = hashes.SHA256()
ecdsa_prehash = ec.ECDSA(utils.Prehashed(chosen_hash))

def hash(data):
    hasher = hashes.Hash(chosen_hash, default_backend())
    hasher.update(data)
    digest = hasher.finalize()
    return digest

def sign(private_key, data):
    digest = hash(data)
    signature = private_key.sign(digest, ecdsa_prehash)
    return signature

def verify(public_key, signature, data):
    try:
        public_key.verify(signature, hash(data), ecdsa_prehash)
        return True
    except InvalidSignature:
        return False

def generate_private_key():
    return ec.generate_private_key(ec.SECP256K1, default_backend())

if __name__ == "__main__":
    private_key = generate_private_key()
    print(private_key)

    data = "maya hee, maya hoo, maya hehe".encode("utf8")
    print(data)

    signature = sign(private_key, data)
    print(signature)

    public_key = private_key.public_key()
    print(public_key)

    print(verify(public_key, signature, data))