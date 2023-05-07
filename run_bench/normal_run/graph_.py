import igraph
import sys, os
from time import time, sleep
import subprocess
from datetime import datetime
import random
import shutil

CUR_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
graph_dir = CUR_DIR + "/graph_dir"
VTUNE = "/opt/intel/oneapi/vtune/2023.1.0/bin64/vtune"
PROF_DIR_BASE= "/home/cc/functions/run_bench/vtune_log"

def main():

    algo = sys.argv[1]
    size = sys.argv[2]
    run_vtune = sys.argv[3]
    get_heatmap = sys.argv[4]

    # gen graph
    graph_generating_begin = time()
    # graph = igraph.Graph.Barabasi(int(size), 10)
    graph_gen_time = time() - graph_generating_begin

    # read graph
    start_loading = time()
    if size == "twitter" or size == "COLLAB_A" or size == "aspirin_A" or size == "twitter_rv" :
        file_name = graph_dir + "/" + size + ".el"
        graph = igraph.Graph.Read(f=file_name, format="edgelist")
    else:
        file_name = graph_dir + "/" + size + ".pkl"
        graph = igraph.Graph.Read(f=file_name, format="pickle")
    read_time = time() - start_loading
    print("VA of graph:", hex(id(graph)), "decimal is: ", id(graph))

    # compute
    check_pid = str(os.getpid())
    if get_heatmap == "true":
        damo_trace = "/home/cc/functions/run_bench/playground/"+ algo + "_" + size + "/" + algo + "_" + size + ".data"
        subprocess.Popen(["sudo","/home/cc/damo/damo","record", "--monitoring_nr_regions_range", "1000", "2000", "-o", 
                        damo_trace, check_pid])
    if run_vtune == "true":
        PROF_DIR = os.path.join(PROF_DIR_BASE, algo + "_" + size)
        if os.path.isdir(PROF_DIR):
            shutil.rmtree(PROF_DIR)
        subprocess.Popen([VTUNE, "-collect", "uarch-exploration", "-r", 
                          PROF_DIR, "-target-pid", check_pid])
    process_begin = time()
    cur_nanosec = int((process_begin - int(process_begin)) * 1e9)
    print("start computing from: {}.{}".format(int(process_begin), cur_nanosec))

    if algo == 'pagerank':
        result = graph.pagerank()
    elif algo == 'mst':
        result = graph.spanning_tree(None, False)
    elif algo == 'bfs':
        result = graph.bfs(0)
    elif algo == 'clusters':
        result = graph.clusters(mode='strong')
    elif algo == 'biconnect':
        result = graph.biconnected_components()
    else: 
        print("unsupported algo!")
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
    
def dump_graph():
    size = "twitter_rv"
    graph_generating_begin = time()
    graph = igraph.Graph.Barabasi(int(size), 10)
    graph_gen_time = time() - graph_generating_begin

    graph_dump_begin = time()

    # print(g)
    # graph.write_edgelist(f=graph_dir+"/{}.el".format(size))
    # graph.write_pickle(fname="/home/cc/functions/run_bench/normal_run/graph_dir/{}.pkl".format(size))
    # graph.write_graphmlz(f="/home/cc/functions/run_bench/normal_run/graph_dir/{}_graphmlz".format(size), compresslevel=9)
    # graph_graphmlz = igraph.Graph.Read_GraphMLz(f=graph_dir + "/{}_graphmlz".format(size))
    graph_dump_time = time() - graph_dump_begin

    graph_pickle_read_begin = time()
    graph_pickle = igraph.Graph.Read(f=graph_dir + "/{}.el".format(size), format="edgelist")
    # graph_pickle = igraph.Graph.Read(f=graph_dir + "/{}.pkl".format(size), format="pickle")
    graph_pickle_load_time = time() - graph_pickle_read_begin

    print("graph_gen_time: ", "{:.2f}".format(graph_gen_time),
        "graph_dump_time: ", "{:.2f}".format(graph_dump_time),
        "graph_picke_load_time: ", "{:.2f}".format(graph_pickle_load_time))
    process_begin = time()
    graph_pickle.pagerank()
    pr_done = time()
    print("pr:", pr_done - process_begin)
    graph_pickle.spanning_tree(None, False)
    mst_done = time()
    print("mst:", mst_done - pr_done)
    graph_pickle.bfs(0)
    graph_pickle.mincut(None, None, None)
    bfs_done = time()
    print("bfs:", bfs_done - mst_done)
    graph_pickle.biconnected_components()
    biconnect_done = time()
    print("biconnect:", biconnect_done - bfs_done)

main()
# dump_graph()
