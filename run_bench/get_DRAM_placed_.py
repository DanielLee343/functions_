import os, sys

workload_name = sys.argv[1]
intercepted_log = "/home/cc/functions/run_bench/playground/{}/intercepted.log".format(workload_name)

dram_binded = {} #{"mmap start addr": "size"}
dram_binded_tuples = set()
with open(intercepted_log, 'r') as file:
    for line in file:
        if line.startswith('node0'):
            splitted = [item.strip() for item in line.split(',') if item.strip() != ""]
            start_addr = int(splitted[1])
            dram_bind_value = int(splitted[2])
            end_addr = start_addr + dram_bind_value
            dram_binded_tuples.add((start_addr, end_addr))

while True:
    merged = set()
    for tuple1 in dram_binded_tuples:
        remaining_counter = len(dram_binded_tuples) - 1
        for tuple2 in dram_binded_tuples:
            if tuple1 != tuple2:
                if tuple1[1] >= tuple2[0] and tuple1[0] <= tuple2[1]:
                    merged.add((min(tuple1[0], tuple2[0]), max(tuple1[1], tuple2[1])))
                else:
                    remaining_counter -= 1
        if remaining_counter == 0:
            merged.add(tuple1)
    if merged == dram_binded_tuples:
        break
    else:
        dram_binded_tuples = merged.copy()

print(len(dram_binded_tuples))
to_dram_bytes = 0
for tp in dram_binded_tuples:
    to_dram_bytes += tp[1] - tp[0]
print("binded to dram for {} is {:.2f} MB".format(workload_name, to_dram_bytes/1024/1024))