import os, sys

workload_name = sys.argv[1]
intercepted_log = "/home/cc/functions/run_bench/playground/{}/intercepted.log".format(workload_name)

dram_binded = {} #{"mmap start addr": "size"}
with open(intercepted_log, 'r') as file:
    for line in file:
        if line.startswith('node0'):
            splitted = [item.strip() for item in line.split(',') if item.strip() != ""]
            start_addr = splitted[1]
            dram_bind_value = int(splitted[2])
            if start_addr not in dram_binded:
                dram_binded[start_addr] = dram_bind_value
            else:
                if dram_bind_value > dram_binded[start_addr]:
                    dram_binded[start_addr] = dram_bind_value
print(len(dram_binded))
to_dram_bytes = sum(dram_binded.values())
print("binded to dram for {} is {:.2f} MB".format(workload_name, to_dram_bytes/1024/1024))