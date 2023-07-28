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
    file_to_process = sys.argv[1] # xx_bw_raw.csv
    workload_name = sys.argv[2] # xx
    bw_or_fp = sys.argv[3] # bandwidth or footprint
    output_dir = os.path.dirname(file_to_process)
    
    if bw_or_fp == "bw":
        cur_df = pd.read_csv(file_to_process)
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
    elif bw_or_fp == "fp":
        import re
        import numpy as np
        from matplotlib import pyplot as plt
        dram_fp = []
        cxl_fp = []
        index = 0
        start_dram = 0
        start_cxl = 0
        with open(file_to_process, 'r') as file:
            for line in file:
                if line.startswith('node 0 free:'):
                    match = re.search(r":\s*([\d.]+)\s*MB", line)
                    if match:
                        value = match.group(1)
                        if index == 0:
                            start_dram = int(value)
                        dram_fp.append(start_dram - int(value))
                elif line.startswith('node 1 free:'):
                    match = re.search(r":\s*([\d.]+)\s*MB", line)
                    if match:
                        value = match.group(1)
                        if index == 0:
                            start_cxl = int(value)
                            index = 1
                        cxl_fp.append(start_cxl - int(value))
        # start_dram = max(dram_fp)
        # start_cxl = max(cxl_fp)
        # dram_fp = [start_dram - x for x in dram_fp]
        # cxl_fp = [start_cxl - x for x in cxl_fp]
        x_range = np.arange(1, len(dram_fp) + 1) / 10
        fig, ax = plt.subplots()
        # plt.xlim(0, 6)
        plt.ylim(min(dram_fp + cxl_fp), max(dram_fp + cxl_fp))
        ax.plot(x_range, dram_fp, label='DRAM (MB)')
        ax.plot(x_range, cxl_fp, label='CXL (MB)')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Memory Footprint (MB)')
        ax.legend()
        ax.set_title('memory footprint of {}'.format(workload_name))
        output_cdf = os.path.join(output_dir, workload_name + "_mem_fp.png")
        plt.savefig(output_cdf)

def test():
    import re
    string = "node 0 free: 85648 MB"
    match = re.search(r":\s*([\d.]+)\s*MB", string)

    if match:
        value = match.group(1)
        print(value)

# test()
main()