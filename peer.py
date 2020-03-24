import os
import sys
from random import randint, random
from time import time
from base64 import b64encode, b64decode

import zmq

from udpbroadcast.server import reip
from udpbroadcast.client import blip, local_ip

from every import Every

from crypto import generate_keys, sign, verify, save_pem_keys, load_pem_keys, public2pem, pem2public
from db import generate_random_tx, make_tx

os.makedirs("keys", exist_ok=True)

global_private_key = global_public_key = None

if len(sys.argv) < 2:
	raise Exception("need key index")

keyindex = sys.argv[1]
keypath = "keys/" + keyindex + ".pem"
result = load_pem_keys(keypath)
if result:
	global_private_key, global_public_key = result

if global_private_key is None:
	global_private_key, global_public_key = generate_keys()
	print("Keypair generated.")
	save_pem_keys(keypath, global_private_key)
	print("Saved key to", keypath)
else:
	print("Loaded key from", keypath)

print(public2pem(global_public_key).decode("utf8"))

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
			#elif typ == "info":
			#	t = time()
			#	public_key = pem2public(data["public_key"].encode("utf8"))
			#	print(t, public_key)
			elif typ == "tx":
				print("Received tx")
				pubkeypem = data["pubkey"].encode("utf8")
				pubkey = pem2public(pubkeypem)
				signature = b64decode(data["signature"])
				datafield = data["data"].encode("utf8")
				verified = verify(pubkey, signature, datafield)
				print("Signature verified: ", verified)
				if verified:
					# watch padding, merkle tree like problem!
					#metasignature = sign(global_private_key, b"\n".join([pubkeypem, data["signature"].encode("utf8"), datafield]))
					targetpem, value = data["data"].split("\t")
					value = int(value)
					print("MAKETX:", make_tx(data["pubkey"], targetpem, value))


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

		#pub.send_json({"type":"info", "data":{"public_key":public2pem(global_public_key).decode("utf8")}})


		targetpem, value = generate_random_tx(public2pem(global_public_key).decode("utf8"))
		data = targetpem + "\t" + str(value)
		signature = sign(global_private_key, data.encode("utf8"))
		signature = b64encode(signature).decode("utf8")
		print(signature)

		pub.send_json({"type":"tx", "data": {"pubkey": public2pem(global_public_key).decode("utf8"), "signature": signature, "data":data}})

	if everysec:
		pub.send_json({"type":"peers", "data":peerlist})

		pub.send_json({"type":"data", "data":consdata})

		blip(txpath)

		msg = reip(0.5+random())

		if msg is not None:
			connect(msg)
