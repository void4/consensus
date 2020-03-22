from random import randint

import zmq

from udpbroadcast.server import reip
from udpbroadcast.client import blip, local_ip

from every import Every

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

sublist = []

everysec = Every(1)
every5sec = Every(5)

consdata = randint(0, 255)

def connect(path):
	sub.connect(path)
	sublist.append(path)

while True:

	try:
		if sublist:
			msg = sub.recv_json(zmq.NOBLOCK)
			#print("recv", msg)
			typ = msg["type"]
			data = msg["data"]

			if typ == "chat":
				print(data)
			elif typ == "peers":
				for peer in data:
					if peer not in sublist:
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
		pub.send_json({"type":"chat", "data":"test"})
		print("Sent.")

	if everysec:
		pub.send_json({"type":"peers", "data":sublist})

		pub.send_json({"type":"data", "data":consdata})

		blip(txpath)

		msg = reip(0.5)

		if msg is not None:
			txp = msg#msg.split("\t")
			if txp != txpath and txp not in sublist:#rxp != rxpath and
				print("FOUND NEW PEER")
				connect(txp)
				print("Connected to", txp)
