import base64
import struct


# significant to float
def s_to_f(significand: int) -> float:
    base = 10
    exponent = -2
    return significand * base**exponent

# decode the data from base64
raw = base64.b64decode("NAkAALoLAAA=")

# unpack 2 little-endian 4-byte signed integer
t, h = struct.unpack("<ii", raw)

print(f"Temp: {s_to_f(t)} C\nHumidity: {s_to_f(h)} %")
