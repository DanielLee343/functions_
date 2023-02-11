

filename = "./log_of_sos_bm/log_from_numamaps_3.txt"
so_set = set()
with open(filename) as file:
    for line in file:
        file=line.rstrip().split(' ')[2] # result: file=xxx
        file=file[5:]
        so_set.add(file)
print(so_set)

with open('./to_evict_bm.txt', 'w') as f:
    for line in so_set:
        f.write(f"{line}\n")