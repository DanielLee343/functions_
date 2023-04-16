import igraph
import sys, os
from time import time, sleep
import subprocess
from datetime import datetime

CUR_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
graph_dir = CUR_DIR + "/graph_dir"

def main():
    algo = sys.argv[1]
    size = sys.argv[2]
    file_name = graph_dir + "/" + size + ".pkl"

    # gen graph
    graph_generating_begin = time()
    # graph = igraph.Graph.Barabasi(int(size), 10)
    graph_gen_time = time() - graph_generating_begin

    # read graph
    start_loading = time()
    graph = igraph.Graph.Read(f=file_name, format="pickle") # mmap() -> 30s
    read_time = time() - start_loading
    print("VA of graph:", hex(id(graph)))

    # compute
    check_pid = str(os.getpid())
    subprocess.Popen(["sudo","damo","record", "--monitoring_nr_regions_range", "1000", "2000", "-o", 
                        "/home/cc/functions/run_bench/playground/"+algo+"/"+algo+".data", check_pid])
    process_begin = time()

    # now = datetime.now()
    # current_time = now.strftime("%H:%M:%S")
    # print("start computing =", current_time)

    if algo == 'pagerank':
        result = graph.pagerank()
    elif algo == 'mst':
        result = graph.spanning_tree(None, False)
    elif algo == 'bfs':
        result = graph.bfs(0)
    else: 
        print("wrong algo!")
        return "err"
    process_time = time() - process_begin
    # now = datetime.now()
    # current_time = now.strftime("%H:%M:%S")
    # print("finish computing =", current_time)

    # dump graph
    dump_start = time()
    # graph.write(f=file_name, format="pickle")
    dump_time = time() - dump_start
    
    print("graph_generating_time: ", "{:.2f}".format(graph_gen_time),
        "dump_time: ", "{:.2f}".format(dump_time),
        "read_time: ", "{:.2f}".format(read_time),
        "compute_time: ", "{:.2f}".format(process_time))
    
main()