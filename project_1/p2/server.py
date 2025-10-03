import base64
import socket
import struct
import threading

HOST = "127.0.0.1"  # Symbolic name meaning all available interfaces
PORT = 50007  # Arbitrary non-privileged port
PACKET_SIZE = 8
BASE64_SIZE = 12
BASE = 10
EXPONENT = -2

# Endianness
# Different architectures interpret data differently
#   < - little endian: lowest order byte first (x86, x86_64, Arm)
#   > - big endian: highest order byte comes first (PowerPC, SPARC)
#  Potential improvement could be:
#   - using 'network byte order' (big endian)
#   - using BOM (add an identifier before all values)
#  Another practical improvement if you don't know what data is coming
#  could be checking the values to see if they are reasonable

# Optimization
# Signed 16-bit integer (int16)
# Range: -32768 … 32767
# -> Use int16 (2 bytes)
# Another optimization would be to send raw bytes instead of ASCII
# since ASCII inflates data size by 33% in this case (12 bytes for ASCII vs 8 raw bytes)

# Why aren't we just sending the data in a human readable format?
# Sending text characters would use more space!
# Sensors/edge devices may be simple without such functionality or unwanted wasted resources
# Binary values are not possible to interpret wrong (except endianness)

# Sending arbitrary amount of data
# - establish protocol to send length first then receive data
#   -> first header with data length always same size, then data
# - using a delimiter; parse chunks of data and split using agreed upon delimiter


def client(conn: socket.socket, addr: tuple[str, int]) -> None:
    with conn:
        data = conn.recv(BASE64_SIZE)
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

        t = round(v1 * BASE**EXPONENT, 2)
        h = round(v2 * BASE**EXPONENT, 2)

        print(f"\n** Received from {addr[0]} **\nTemperature: {t} C\nHumidity: {h} %")  # noqa: T201
        conn.sendall(b"Ok")


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # force reuse port
    s.bind((HOST, PORT))
    s.listen(1)

    # add simple multi-threading
    while True:
        conn, addr = s.accept()
        threading.Thread(target=client, args=(conn, addr), daemon=True).start()
