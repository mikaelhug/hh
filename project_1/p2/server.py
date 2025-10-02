import base64
import socket
import struct
import threading

HOST = "127.0.0.1"  # Symbolic name meaning all available interfaces
PORT = 50007  # Arbitrary non-privileged port
PACKET_SIZE = 8
BASE = 10
EXPONENT = -2


def client(conn: socket.socket, addr: tuple[str, int]) -> None:
    with conn:
        data = conn.recv(1024)
        if not data:
            conn.sendall(b"No data received")
            return

        # decode the data from base64
        try:
            raw = base64.b64decode(data)
        except ValueError as e:
            msg = f"Error: {e}".encode()
            conn.sendall(msg)
            return

        # check package length
        if len(raw) != PACKET_SIZE:
            conn.sendall(b"Wrong package length")
            return

        # unpack 2 little-endian 4-byte signed integer
        try:
            v1, v2 = struct.unpack("<ii", raw)
        except ValueError as e:
            msg = f"Invalid struct: {e}".encode()
            conn.sendall(msg)
            return

        t = v1 * BASE**EXPONENT
        h = v2 * BASE**EXPONENT

        print(f"\n** Received from {addr[0]} **\nTemp: {t} C\nHumidity: {h} %")  # noqa: T201
        conn.sendall(b"Ok")


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # force reuse port
    s.bind((HOST, PORT))
    s.listen(1)

    # add simple multi-threading
    while True:
        conn, addr = s.accept()
        threading.Thread(target=client, args=(conn, addr), daemon=True).start()
