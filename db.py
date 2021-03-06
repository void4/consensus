from random import choice

from tinydb import TinyDB, Query

from genesis import zero

#temporary file, multiple clients same directory!

db = None

def load_genesis():
    for pempubkey, value in zero.items():
        db.insert({"pubkey": pempubkey, "value": int(value)})



def init_db(id):
    global db
    db = TinyDB(f"db-{id}.json")

    if len(db.all()) == 0:
        load_genesis()
        print("Loaded genesis into db")

#db.purge()

def generate_random_tx(pempubkey):
    randomitem = choice(db.all())
    targetpem = randomitem["pubkey"]
    value = db.search(Query().pubkey==pempubkey)[0]["value"] // 2
    return [targetpem, value]

#def verify_tx(signature, )

def make_tx(pemsource, pemtarget, value):
    if value < 0:
        return "Cannot send negative value"

    # Need to be very careful here
    if pemsource == pemtarget:
        return "Can't send to oneself"

    #race condition?
    sourcequery = Query().pubkey==pemsource
    targetquery = Query().pubkey==pemtarget

    sourcevalue = db.search(sourcequery)[0]["value"]

    if value > sourcevalue:
        return "Insufficient funds"

    print("TRANSFER", sourcevalue, targetvalue, value)
    db.update({"value": sourcevalue-value}, sourcequery)

    targetvalue = db.search(targetquery)

    if len(targetvalue) > 0:
        db.update({"value": targetvalue[0]["value"]+value}, targetquery)
    else:
        db.insert({"pubkey": pemtarget, "value": value})



    return True

def dbprint():
    for item in db.all():
        print(item["pubkey"].split("\n")[-2][-8:], ":", item["value"])
