from glob import glob
from crypto import load_pem_keys, public2pem

for keypath in sorted(glob("keys/*.pem")):
    privkey, pubkey = load_pem_keys(keypath)
    print(public2pem(pubkey).decode("utf8"))
