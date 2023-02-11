# !/usr/bin/python3

import re
import glob
import os
import sys
import csv

print(sys.argv[1])
N0_list = []
N1_list = []
filelist = os.listdir("/home/cc/functions/run_bench/numa_dstb_res_"+sys.argv[1])
for infile in sorted(filelist): 
    print(str(infile))
    filename = "/home/cc/functions/run_bench/numa_dstb_res_"+sys.argv[1]+"/"+str(infile)
    N0_sum_cur = 0
    N1_sum_cur = 0
    with open(filename) as file:
        for line in file:
            line_list = line.rstrip().split(" ")
            for id in line_list:
                if id.startswith("N1"):
                    N1_sum_cur += int(id[3:])
                elif id.startswith("N0"):
                    N0_sum_cur += int(id[3:])
    N0_list.append(N0_sum_cur)
    N1_list.append(N1_sum_cur)
    print("N0: ", N0_sum_cur)
    print("N1: ", N1_sum_cur)

# write to csv
with open("python_evict_bm_dstb_only_sos.csv", "w") as csvfile:
    wr = csv.writer(csvfile, delimiter = ',')
    wr.writerow(['node0', 'node1'])
    for i in range(len(N0_list)):
        wr.writerow([N0_list[i], N1_list[i]])