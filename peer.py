from random import randint, random

import zmq

from udpbroadcast.server import reip
from udpbroadcast.client import blip, local_ip

from every import Every

from crypto import generate_private_key, sign, verify

private_key = generate_private_key()
print("Private key generated.")

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

peerlist = []

everysec = Every(1)
every5sec = Every(5)

consdata = randint(0, 255)

def connect(path):
	if path != txpath and path not in peerlist:
		sub.connect(path)
		peerlist.append(path)
		print("FOUND NEW PEER")
		print("Connected to", path)

while True:

	try:
		if peerlist:
			msg = sub.recv_json(zmq.NOBLOCK)
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
		print(peerlist)

	if everysec:
		pub.send_json({"type":"peers", "data":peerlist})

		pub.send_json({"type":"data", "data":consdata})

		blip(txpath)

		msg = reip(0.5+random())

		if msg is not None:
			connect(msg)
