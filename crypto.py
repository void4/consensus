from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.exceptions import InvalidSignature

chosen_hash = hashes.SHA256()
ecdsa_prehash = ec.ECDSA(utils.Prehashed(chosen_hash))

def public2pem(public_key):
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

def private2pem(private_key):
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

def pem2public(pem):
    return serialization.load_pem_public_key(pem, backend=default_backend())

def pem2private(pem, password=None):
    return serialization.load_pem_private_key(pem, password=password, backend=default_backend())

def load_pem_keys(path):
    try:
        with open(path, "r") as pemfile:
            private_key = pem2private(pemfile.read().encode("utf8"))
            public_key = private_key.public_key()
            print("Loaded key from", path)
            return (private_key, public_key)
    except FileNotFoundError:
        return None

def save_pem_keys(path, private_key):
    with open(path, "w+") as pemfile:
        pemfile.write(private2pem(private_key).decode("utf8"))
    print("Saved key to", path)

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

def generate_keys():
    private_key = generate_private_key()
    public_key = private_key.public_key()
    return private_key, public_key

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

    print(save_pem_private(private_key))
    print(save_pem_public(public_key))
