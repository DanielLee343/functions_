# import numpy as np
# from time import time
# import json
import sys
# import os
import time
# import subprocess
# import mkl

# mkl.set_num_threads(1)

# def matmul(n):
#     A = np.random.rand(n, n)
#     B = np.random.rand(n, n)

#     start = time()
#     C = np.matmul(A, B)
#     latency = time() - start
#     return latency

# def main():
#     # os.environ["OMP_NUM_THREADS"] = "3"
#     n = int(sys.argv[1])
#     result = matmul(n)
#     print(result)
#     return result

# if __name__ == '__main__':
#     main()
# pid = os.getpid()
# result = subprocess.run(['lsof', '-p', str(pid)], stdout=subprocess.PIPE)
# print(result.stdout.decode('utf-8'))
# os.system('sudo lsof -p '+str(pid)+' > before')
# time.sleep(2)

import numpy as np
# import psutil
# print("start matmul..")
# os.system('lsof -p '+str(pid)+' > after')
# current_process = psutil.Process()

n = int(sys.argv[1])

A = np.random.rand(n, n)
B = np.random.rand(n, n)
# os.system('sudo lsof -p '+str(pid)+' > after')

start = time.time()
C = np.matmul(A, B)
latency = time.time() - start
print("latency: ", latency)


# children = current_process.children(recursive=True)
# for child in children:
#     print('Child pid is {}'.format(child.pid))
# os.system('lsof -p '+str(pid)+' > after_matmul')