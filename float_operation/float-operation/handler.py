import math
from time import time
import json

def float_operations(n):
    start = time()
    for i in range(0, n):
        sin_i = math.sin(i)
        cos_i = math.cos(i)
        sqrt_i = math.sqrt(i)
    latency = time() - start
    return latency


def handle(event):
    payload = json.loads(event)
    # print("payload:", payload)
    n = int(payload["n"])
    # print("n:", n)
    result = float_operations(n)
    print(result)
    return result