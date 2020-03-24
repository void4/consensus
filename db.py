from random import choice

from tinydb import TinyDB, Query

from genesis import zero

#temporary file, multiple clients same directory!
db = TinyDB("db.json")

def load_genesis():
    for pempubkey, value in zero.items():
        db.insert({"pubkey": pempubkey, "value": int(value)})


if len(db.all()) == 0:
    load_genesis()
    print("Loaded genesis into db")

#db.purge()

def generate_random_tx(pempubkey):
    print(pempubkey)
    for item in db.all():
        print(item["pubkey"]==pempubkey, item["pubkey"], pempubkey)
    randomitem = choice(db.all())
    targetpem = randomitem["pubkey"]
    value = db.search(Query().pubkey==pempubkey)[0]["value"] // 2
    return [targetpem, value]

#def verify_tx(signature, )

def make_tx(pemsource, pemtarget, value):
    if value < 0:
        return "Cannot send negative value"

    #race condition?
    sourcequery = Query().pubkey==pemsource
    targetquery = Query().pubkey==pemtarget

    sourcevalue = db.search(sourcequery)[0]["value"]

    if value > sourcevalue:
        return "Insufficient funds"

    targetvalue = db.search(targetquery)[0]["value"]

    db.update({"value": sourcevalue-value}, sourcequery)
    db.update({"value": targetvalue+value}, targetquery)

    return True
