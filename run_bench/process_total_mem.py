import pandas as pd
import os
import csv
from itertools import zip_longest
import glob
import sys
import re

os.chdir("./normal_run")
func = sys.argv[1] # matmul
all_cols = []
header = []
data = {}
org_df = pd.DataFrame()

for file in glob.glob(func+"*.csv"):
    print(file)
    # get n, and append to header
    n = re.search(func+'_(.*).csv', file)
    n = n.group(1)
    # header.append(n)
    # read csv
    cur_df = pd.read_csv(file)
    # print(cur_df)
    # print(cur_df.iloc[:, 1])
    memory_usage_df = cur_df.iloc[:, 1]
    # convert df to list
    memory_usage_list = memory_usage_df.tolist()
    # data[n] = memory_usage_list
    # all_cols.append(memory_usage_list)
    add_df = pd.DataFrame(memory_usage_list, columns=[n])
    org_df = pd.concat([org_df, add_df],axis=1)
    # print(org_df)
# print(data)

# with open(func+"_result.csv", "w") as f:
#     writer = csv.writer(f)
#     writer.writerow(header)
#     for values in zip_longest(*all_cols):
#         writer.writerow(values)

# df = pd.DataFrame(data)
org_df.to_csv(func+"_result.csv")