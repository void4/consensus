from random import randint, random
from time import time
from base64 import b64encode, b64decode

import zmq

from udpbroadcast.server import reip
from udpbroadcast.client import blip, local_ip

from every import Every

from crypto import generate_keys, sign, verify, save_pem_public, load_pem_public

private_key, public_key = generate_keys()
print(save_pem_public(public_key))
print("Keypair generated.")

ctx = zmq.Context()


PROTOCOL = "tcp"

IP = "0.0.0.0"


txpath = f"{PROTOCOL}://{IP}"


pub = ctx.socket(zmq.PUB)
port = pub.bind_to_random_port(txpath)

txpath += f":{port}"
print("PUB", txpath)

sub = ctx.socket(zmq.SUB)
sub.setsockopt(zmq.SUBSCRIBE, b"")

peerlist = {}

everysec = Every(1)
every5sec = Every(5)

consdata = randint(0, 255)

def connect(path):
	if path != txpath and path not in peerlist:
		sub.connect(path)
		peerlist[path] = {}
		print("FOUND NEW PEER")
		print("Connected to", path)

while True:

	try:
		if peerlist:
			msg = sub.recv_json(zmq.NOBLOCK)
			# don't know which publisher sent...
			#print("recv", msg)
			typ = msg["type"]
			data = msg["data"]

			if typ == "chat":
				print(data)
			elif typ == "peers":
				for peer in data:
					connect(peer)
			elif typ == "data":
				consdata = (consdata + data)/2
				print(consdata)
			elif typ == "info":
				t = time()
				public_key = load_pem_public(data["public_key"].encode("utf8"))
				print(t, public_key)
			elif typ == "tx":
				pubkey = load_pem_public(data["pubkey"].encode("utf8"))
				signature = b64decode(data["signature"])
				datafield = data["data"].encode("utf8")
				print("Verification: ", verify(pubkey, signature, datafield))
			else:
				print(msg)

	except zmq.error.Again as e:
		pass
	except zmq.ZMQError as e:
		print(e)
		pass

	if every5sec:
		pub.send_json({"type":"chat", "data":"ping"})
		print("Sent ping.")
		print(f"Have {len(peerlist)} peers.")
		print(peerlist.keys())
		pub.send_json({"type":"info", "data":{"public_key":save_pem_public(public_key).decode("utf8")}})
		data = txpath
		signature = sign(private_key, data.encode("utf8"))
		signature = b64encode(signature).decode("utf8")
		print(signature)

		pub.send_json({"type":"tx", "data": {"pubkey": save_pem_public(public_key).decode("utf8"), "signature": signature, "data":data}})

	if everysec:
		pub.send_json({"type":"peers", "data":peerlist})

		pub.send_json({"type":"data", "data":consdata})

		blip(txpath)

		msg = reip(0.5+random())

		if msg is not None:
			connect(msg)
