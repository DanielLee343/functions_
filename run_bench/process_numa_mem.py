import pandas as pd
import os
import csv
from itertools import zip_longest
import glob
import sys
import re

# func = sys.argv[1] # <matmul>
# env = sys.argv[2] # <base, cxl>
# os.chdir("/home/cc/functions/run_bench/"+func)
os.chdir("/home/cc/functions/run_bench/test_diff")
org_df = pd.DataFrame()

for file in glob.glob("*.csv"):
    print(file)
    # n = re.search(env+'_(.*).csv', file)
    n = re.search('python(.*).csv', file)
    n = n.group(1) # get n
    print(n)
    cur_df = pd.read_csv(file)
    cur_skt_0_mem = cur_df.iloc[:, 13] # column for Memory (MB/s) for sock0
    cur_skt_1_mem = cur_df.iloc[:, 25] # column for Memory (MB/s) for sock1
    cur_skt_0_mem = cur_skt_0_mem.tolist()
    cur_skt_1_mem = cur_skt_1_mem.tolist()
    del cur_skt_0_mem[0]
    del cur_skt_1_mem[0]
    # print(cur_skt_0_mem)
    # print(cur_skt_1_mem)
    cur_mem = {n+"_sock0": cur_skt_0_mem, n+"_sock1": cur_skt_1_mem}
    add_df = pd.DataFrame(cur_mem)
    org_df = pd.concat([org_df, add_df],axis=1)

# org_df.to_csv("/home/cc/functions/run_bench/"+func+"/"+func+"_"+env+"_result.csv",index=False)
org_df.to_csv("/home/cc/functions/run_bench/test_diff/result.csv",index=False)