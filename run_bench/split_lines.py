import sys, os
    
def divide_file_into_chunks(workload_dir, workload):
    # workload_dir = "/home/cc/functions/run_bench/playground/{}".format(workload)
    filepath = workload_dir + "/abs_addr_time.txt"
    with open(filepath, 'r') as file:
        lines = file.readlines()
        lines_per_chunk = len(lines) // 3
        chunks = [lines[i:i+lines_per_chunk] for i in range(0, len(lines), lines_per_chunk)]
        for i, chunk in enumerate(chunks):
            chunk_filename = f'{workload_dir}/{workload}_{i}.txt'

            with open(chunk_filename, 'w') as chunk_file:
                chunk_file.writelines(chunk)

def truncate_file(workload_dir, lines_to_keep):
    # workload_dir = "/home/cc/functions/run_bench/playground/{}".format(workload)
    for i in range(3):
        filepath = workload_dir + f"/chunk_{i}.txt"
        # print(filepath)
        with open(filepath, 'r+') as file:
            lines = file.readlines()
            file.seek(0)
            file.truncate()
            file.writelines(lines[:lines_to_keep])

def concatenate_files(workload_dir, workload):
    file1 = workload_dir + f'/{workload}_0.txt'
    file2 = workload_dir + f'/{workload}_1.txt'
    file3 = workload_dir + f'/{workload}_2.txt'
    output_file = workload_dir + "/abs_addr_time.txt"
    with open(output_file, 'w') as outfile:
        # Read the content of each file and write it to the output file
        for filename in [file1, file2, file3]:
            with open(filename, 'r') as infile:
                outfile.write(infile.read())

workload = sys.argv[1]
workload_dir = "/home/cc/functions/run_bench/playground/{}".format(workload)
# filepath = "/home/cc/functions/run_bench/playground/{}/abs_addr_time.txt".format(workload)
divide_file_into_chunks(workload_dir, workload)
if workload == "gif":
    lines_to_keep = -6000
    truncate_file(workload_dir, lines_to_keep)
    concatenate_files(workload_dir)
    