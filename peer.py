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

while True:

	try:
		if sublist:
			msg = sub.recv_string(zmq.NOBLOCK)
			print("recv", msg)
	except zmq.error.Again as e:
		pass
	except zmq.ZMQError as e:
		print(e)
		pass

	if every5sec:
		pub.send_string("test")
		print("Sent.")

	if everysec:
		blip(txpath)

		msg = reip(0.5)

		if msg is not None:
			txp = msg#msg.split("\t")
			if txp != txpath and txp not in sublist:#rxp != rxpath and
				print("FOUND NEW PEER")
				sublist.append(txp)
				sub.connect(txp)
				print("Connected to", txp)
