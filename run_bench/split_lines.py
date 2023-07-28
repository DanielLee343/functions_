import sys
import os


def divide_file_into_chunks(workload_dir, workload, num_chunk):
    # workload_dir = "/home/cc/functions/run_bench/playground/{}".format(workload)
    filepath = workload_dir + "/abs_addr_time.txt"
    with open(filepath, 'r') as file:
        lines = file.readlines()
        lines_per_chunk = len(lines) // num_chunk
        chunks = [lines[i:i+lines_per_chunk]
                  for i in range(0, len(lines), lines_per_chunk)]
        for i, chunk in enumerate(chunks):
            chunk_filename = f'{workload_dir}/{workload}_{i}.txt'

            with open(chunk_filename, 'w') as chunk_file:
                chunk_file.writelines(chunk)


def truncate_file(workload_dir, lines_to_keep, workload, num_chunk):
    # workload_dir = "/home/cc/functions/run_bench/playground/{}".format(workload)
    for i in range(num_chunk):
        filepath = workload_dir + f'/{workload}_{i}.txt'
        # print(filepath)
        with open(filepath, 'r+') as file:
            lines = file.readlines()
            file.seek(0)
            file.truncate()
            file.writelines(lines[:lines_to_keep])


def concatenate_files(workload_dir, workload, num_chunk):
    all_splited_files = []
    output_file = workload_dir + "/abs_addr_time.txt"
    for i in range(num_chunk):
        cur_file_name = workload_dir + f'/{workload}_{i}.txt'
        all_splited_files.append(cur_file_name)
    # file1 = workload_dir + f'/{workload}_0.txt'
    # file2 = workload_dir + f'/{workload}_1.txt'
    # file3 = workload_dir + f'/{workload}_2.txt'
    # file4 = workload_dir + f'/{workload}_3.txt'
    with open(output_file, 'w') as outfile:
        # Read the content of each file and write it to the output file
        for filename in all_splited_files:
            with open(filename, 'r') as infile:
                outfile.write(infile.read())


workload = sys.argv[1]
num_regions = int(sys.argv[2])
workload_dir = "/home/cc/functions/run_bench/playground/{}".format(workload)
# filepath = "/home/cc/functions/run_bench/playground/{}/abs_addr_time.txt".format(workload)
divide_file_into_chunks(workload_dir, workload, num_regions)
if workload == "gif":
    lines_to_keep = -6000
    truncate_file(workload_dir, lines_to_keep, workload, num_regions)
    concatenate_files(workload_dir, workload, num_regions)
