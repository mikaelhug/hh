import base64
import random
import socket
import struct
import time

BASE64_SIZE = 12

while True:
    # generate random temperature and humidity
    rand_tem = random.randint(-5000, 12000)  # noqa: S311
    rand_hum = random.randint(0, 10000)  # noqa: S311
    print(f"\n** Sending **\nTemperature: {rand_tem / 100} C\nHumidity: {rand_hum / 100} %")
    packed = struct.pack("<ii", rand_tem, rand_hum)
    encoded = base64.b64encode(packed)

    HOST = "127.0.0.1"  # The remote host
    PORT = 50007  # The same port as used by the server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(encoded)
        data = s.recv(BASE64_SIZE)

    if repr(data) != "b'Ok'":
        print("Received", repr(data))
    time.sleep(10)
