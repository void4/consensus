from socket import *



def reip(to=5):

    sock = socket(AF_INET, SOCK_DGRAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    sock.bind(("", 12345))

    sock.settimeout(to)
    try:
        msg = sock.recvfrom(1024)
    except timeout:
        sock.close()
        return
    decoded = msg[0].decode("utf8")
    #print(decoded)
    sock.close()
    return decoded

if __name__ == "__main__":
    reip()
