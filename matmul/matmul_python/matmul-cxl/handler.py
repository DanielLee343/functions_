import numpy as np
from time import time
# import subprocess
import json
import os

def matmul(n):
    A = np.random.rand(n, n)
    B = np.random.rand(n, n)

    start = time()
    C = np.matmul(A, B)
    latency = time() - start
    return latency

# def get_so():
#     pid = os.getpid() # int
#     result = subprocess.run(['lsof', '-p', str(pid)], stdout=subprocess.PIPE)
#     print(result.stdout.decode('utf-8'))
    # os.system('lsof -p '+str(pid))

def handle(req):
    payload = json.loads(req)
    n = int(payload['n'])
    result = matmul(n)
    # get_so()
    print(result)
    return result