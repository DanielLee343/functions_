import os
import sys
import time

workload_name = sys.argv[1]
thresh = sys.argv[2]
intercepted_log = "/home/cc/functions/run_bench/playground/{}/intercepted_{}.log".format(
    workload_name, thresh)

dram_binded = {}  # {"mmap start addr": "size"}
dram_binded_tuples = set()
with open(intercepted_log, 'r') as file:
    for line in file:
        if line.startswith('node0'):
            splitted = [item.strip()
                        for item in line.split(',') if item.strip() != ""]
            start_addr = int(splitted[1])
            dram_bind_value = int(splitted[2])
            end_addr = start_addr + dram_bind_value
            dram_binded_tuples.add((start_addr, end_addr))
if len(dram_binded_tuples) == 0:
    print("no dram regions")
    exit(0)

# file_path = "/home/cc/functions/run_bench/test_dram_placed.txt"
# with open(file_path, "w") as file:
#     # Iterate over the list and write each tuple to a new line
#     for tpl in dram_binded_tuples:
#         line = ' '.join(str(x) for x in tpl) + '\n'
#         file.write(line)

# file_path = "/home/cc/functions/run_bench/test_dram_placed.txt"
# dram_binded_tuples = set()
# with open(file_path, "r") as file:
#     for line in file:
#         if line.strip() == "":
#             break
#         cur_tuple = [item.strip()
#                         for item in line.split(' ') if item.strip() != ""]
#         start = int(cur_tuple[0])
#         end = int(cur_tuple[1])
#         dram_binded_tuples.add((start, end))
# print(dram_binded_tuples)

def merge_ranges_fast(ranges):
    # Sort the ranges based on the start value
    sorted_ranges = sorted(ranges, key=lambda x: x[0])
    # print(len(sorted_ranges))
    
    merged_ranges = set()
    current_range = sorted_ranges[0]
    
    for next_range in sorted_ranges[1:]:
        if next_range[0] <= current_range[1]:
            # Overlapping or adjacent ranges, update the end value
            current_range = (current_range[0], max(current_range[1], next_range[1]))
        else:
            # Non-overlapping range, add the current range to the merged list
            merged_ranges.add(current_range)
            current_range = next_range
    
    # Add the last remaining range to the merged list
    merged_ranges.add(current_range)
    
    return merged_ranges

merged_fast = merge_ranges_fast(dram_binded_tuples)
print("len(merged_fast):", len(merged_fast))
# print("merged_fast:", merged_fast)
# while True:
#     merged = set()
#     for tuple1 in dram_binded_tuples:
#         # print(tuple1)
#         remaining_counter = len(dram_binded_tuples) - 1
#         for tuple2 in dram_binded_tuples:
#             if tuple1 != tuple2:
#                 if tuple1[1] >= tuple2[0] and tuple1[0] <= tuple2[1]:
#                     # print("found intersection")
#                     merged.add(
#                         (min(tuple1[0], tuple2[0]), max(tuple1[1], tuple2[1])))
#                 else:
#                     # print("not found")
#                     remaining_counter -= 1
#         if remaining_counter == 0:
#             # print("adding standalone")
#             merged.add(tuple1)
#     if merged == dram_binded_tuples:
#         break
#     else:
#         print(len(merged))
#         dram_binded_tuples = merged.copy()

# print("len(merged_slow):", len(dram_binded_tuples))
to_dram_bytes = 0
for tp in dram_binded_tuples:
    to_dram_bytes += tp[1] - tp[0]
print("binded to dram for {} is {:.2f} MB".format(
    workload_name, to_dram_bytes/1024/1024))