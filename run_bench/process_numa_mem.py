import pandas as pd
import os
import csv
# from itertools import zip_longest
import glob
import sys
# import re

# func = sys.argv[1] # <matmul>
# env = sys.argv[2] # <base, cxl>
# os.chdir("/home/cc/functions/run_bench/"+func)
# os.chdir("/home/cc/functions/run_bench/cifar100_numa_log")
# org_df = pd.DataFrame()

# for file in glob.glob("*.csv"):
#     print(file)
#     # n = re.search(env+'_(.*).csv', file)
#     # n = re.search('python(.*).csv', file)
#     # n = n.group(1) # get n
#     # print(n)
#     cur_df = pd.read_csv(file)
#     cur_skt_0_mem = cur_df.iloc[:, 17] # column for Memory (MB/s) for sock0, 13
#     cur_skt_1_mem = cur_df.iloc[:, 33] # column for Memory (MB/s) for sock1, 25
#     cur_skt_0_mem = cur_skt_0_mem.tolist()
#     cur_skt_1_mem = cur_skt_1_mem.tolist()
#     del cur_skt_0_mem[0]
#     del cur_skt_1_mem[0]
#     # print(cur_skt_0_mem)
#     # print(cur_skt_1_mem)
#     cur_mem = {"sock0": cur_skt_0_mem, "sock1": cur_skt_1_mem}
#     add_df = pd.DataFrame(cur_mem)
#     org_df = pd.concat([org_df, add_df], axis=1)

# org_df.to_csv("/home/cc/functions/run_bench/"+func+"/"+func+"_"+env+"_result.csv",index=False)
# org_df.to_csv("/home/cc/functions/run_bench/cifar100_numa_log/152_result.csv",index=False)

def main():
    pcm_bw_to_process = sys.argv[1] # xx_bw_raw.csv
    workload_name = sys.argv[2] # xx
    output_dir = os.path.dirname(pcm_bw_to_process)
    
    cur_df = pd.read_csv(pcm_bw_to_process)
    cur_skt_0_mem = cur_df.iloc[:, 17] # column for Memory (MB/s) for sock0, 13
    cur_skt_1_mem = cur_df.iloc[:, 33] # column for Memory (MB/s) for sock1, 25
    cur_skt_0_mem = cur_skt_0_mem.tolist()
    cur_skt_1_mem = cur_skt_1_mem.tolist()
    timestamp = []
    for i in range(len(cur_skt_0_mem)):
        timestamp.append(i / 10)
    del timestamp[0]
    del cur_skt_0_mem[0]
    del cur_skt_1_mem[0]
    cur_mem = {"time": timestamp, "sock0": cur_skt_0_mem, "sock1": cur_skt_1_mem}
    # print(timestamp)
    # print(len(timestamp))
    processed_df = pd.DataFrame(cur_mem)

    processed_df.to_csv(output_dir + "/" + workload_name + "_bw.csv", index=False)


def test():
    # print(os.path.basename("/home/cc/functions/run_bench/playground/chameleon/test_wss.png"))
    pcm_bw_to_process = sys.argv[1] # xx_bw_raw.csv
    workload_name = sys.argv[2] # xx
    print(pcm_bw_to_process)
    output_dir = os.path.dirname(pcm_bw_to_process)
    print(output_dir)

# test()
main()