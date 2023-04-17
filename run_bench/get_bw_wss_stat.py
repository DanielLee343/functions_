import os, sys
import pandas as pd
import statistics
import numpy as np
from matplotlib import pyplot as plt

CUR_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))

def get_bw_stat(func_trace_dir, func):
    cur_df = pd.read_csv(os.path.join(func_trace_dir, func + "_bw.csv"))
    cur_skt_0_mem = cur_df.iloc[:, 1] # column for Memory (MB/s) for sock0, 13
    cur_skt_1_mem = cur_df.iloc[:, 2]
    cur_skt_0_mem = cur_skt_0_mem.tolist()
    cur_skt_1_mem = cur_skt_1_mem.tolist()
    print("Median BW of sock0 for {} is {}".format(func, statistics.median(cur_skt_0_mem)))
    print("Median BW of sock1 for {} is {}".format(func, statistics.median(cur_skt_1_mem)))
    print("Max BW of sock0 for {} is {}".format(func, max(cur_skt_0_mem)))
    print("Max BW of sock1 for {} is {}".format(func, max(cur_skt_1_mem)))

    # plot cdf of bw
    # plt.rcParams.update(plt.rcParamsDefault)
    # plt.rcParams["figure.autolayout"] = True
    skt_0_x = np.sort(cur_skt_0_mem)
    skt_0_y = np.arange(1, len(skt_0_x) + 1) / len(skt_0_x)
    skt_1_x = np.sort(cur_skt_1_mem)
    skt_1_y = np.arange(1, len(skt_1_x) + 1) / len(skt_1_x)
    fig, ax = plt.subplots()
    ax.plot(skt_0_x, skt_0_y, label='sock 0')
    ax.plot(skt_1_x, skt_1_y, label='sock 1')
    ax.set_xlabel('Mmeory Bandwidth (MB/s)')
    ax.set_ylabel('CDF')
    ax.legend()
    ax.set_title('CDF of {}'.format(func))
    # plt.grid(False)
    output_cdf = os.path.join(func_trace_dir, func + "_bw_cdf.png")
    plt.savefig(output_cdf)

def gen_wss_cdf(func_trace_dir, func):
    # plt.rcParams.update(plt.rcParamsDefault)
    # plt.rcParams["figure.autolayout"] = True
    input_wss_file = os.path.join(func_trace_dir, func + "_wss.txt")
    with open(input_wss_file, 'r') as file:
        line_index = 0
        all_wss = []
        for line in file:
            if line_index < 4: # get rid of first 4 lines
                line_index += 1
                continue
            line = line.strip().split()
            if line[2] != "MiB":
                continue
            all_wss.append(round(float(line[1])*1.04858, 2)) # convert MiB to MB and remain 2 decimals
            # line_index += 1
    # print(all_wss)
    x = np.sort(all_wss)
    y = np.arange(1, len(x) + 1) / len(x)
    plt.plot(x, y, linestyle='-', color='green')
    plt.xlabel('Working Set Size (MB)')
    plt.ylabel('CDF')
    plt.title('CDF of wss of {}'.format(func))
    plt.grid(False)
    output_cdf = os.path.join(func_trace_dir, func + "_wss_cdf.png")
    plt.savefig(output_cdf)
    
def main():
    func = sys.argv[1]
    wss_or_bw = sys.argv[2]
    func_trace_dir = os.path.join(CUR_DIR, "playground", func)
    if not os.path.exists(func_trace_dir):
        print("wrong input or no such trace")
        return 0
    if wss_or_bw == "wss":
        gen_wss_cdf(func_trace_dir, func)
    plt.rcdefaults()
    if wss_or_bw == "bw":
        get_bw_stat(func_trace_dir, func)

def test():
    plt.rcParams["figure.figsize"] = [7.50, 3.50]
    plt.rcParams["figure.autolayout"] = True

    with open("/home/cc/functions/run_bench/playground/matmul_go/matmul_go_wss.txt",'r') as file:
        line_index = 0
        all_wss = []
        for line in file:
            if line_index < 4: # get rid of first 3 lines
                line_index += 1
                continue
            line = line.strip().split()
            if line[3] != "MiB":
                continue
            all_wss.append(round(float(line[1])*1.04858, 2)) # convert MiB to MB and remain 2 decimals
            # line_index += 1
    print(all_wss)
    # N = 100
    # data = [1, 3, 4, 5, 7, 9, 10, 12, 14, 15, 17, 18, 19, 20, 22, 24, 25, 26, 28, 30]
    x = np.sort(all_wss)
    y = np.arange(1, len(x) + 1) / len(x)
    plt.plot(x, y, marker='o', linestyle='-', color='green')
    plt.xlabel('Working Set Size (MB)')
    plt.ylabel('CDF')
    plt.title('CDF of wss of {}'.format("matmul_go"))
    plt.grid(False)
    # # count, bins_count = np.histogram(data, bins=10)
    # # print(count)
    # # print(bins_count)
    # # pdf = count / sum(count)
    # # cdf = np.cumsum(pdf)
    # # plt.plot(bins_count[1:], cdf, label="CDF")
    # # plt.legend()
    plt.savefig("test.png")
    # plt.show()

main()
# test()