"""Socket Client

Generate ARENA object json and send it to `socket-server.py`.
"""

import random
import socket

from arena import Box, Material

SOCK_SERVER_HOST = "localhost"
SOCK_SERVER_PORT = 8888


def randcolor():
    x = random.randint(0, 255)
    y = random.randint(0, 255)
    z = random.randint(0, 255)
    return (x, y, z)


def main():
    # open socket connection to server
    print("connecting to unsecured generic socket...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SOCK_SERVER_HOST, SOCK_SERVER_PORT))

    # generate random box json
    box = Box(object_id="box", material=Material(color=randcolor()))
    data = box.json()
    print(f"sending unauthenticated {data}")
    sock.sendall(bytes(data, "utf-8"))

    # close socket connection to server
    sock.close()
    print("closed unsecured generic socket.")


if __name__ == "__main__":
    main()
