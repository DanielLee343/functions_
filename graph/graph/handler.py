# import datetime
import igraph
import json, os
from time import time

# CUR_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
graph_dir = "/home/app"

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    payload = json.loads(req)
    algo = payload['algo'] # pagerank, mst, bfs
    size = int(payload['size']) # 1000000, 4000000
    file_name = graph_dir + "/" + str(size) + ".pkl"
    # graph_generating_begin = datetime.datetime.now()
    graph_generating_begin = time()
    # graph = igraph.Graph.Barabasi(size, 10)
    # graph_generating_end = datetime.datetime.now()
    graph_generating_end = time()
    start_loading = time()
    graph = igraph.Graph.Read(f=file_name, format="pickle")
    read_time = time() - start_loading
    print("VA of graph: hex: ", hex(id(graph)), "decimal", id(graph))
    # process_begin = datetime.datetime.now()
    process_begin = time()
    if algo == 'pagerank':
        result = graph.pagerank()
    elif algo == 'mst':
        result = graph.spanning_tree(None, False)
    elif algo == 'bfs':
        result = graph.bfs(0)
    else: 
        print("wrong algo!")
        return "err"
    # process_end = datetime.datetime.now()
    process_end = time()

    # graph_generating_time = (graph_generating_end - graph_generating_begin) / datetime.timedelta(microseconds=1)
    graph_generating_time = graph_generating_end - graph_generating_begin
    # process_time = (process_end - process_begin) / datetime.timedelta(microseconds=1)
    process_time = process_end - process_begin
    return {
        'algo': algo,
        'graph_generating_time': "{:.2f}".format(graph_generating_time),
        'read_graph_time': "{:.2f}".format(read_time),
        'compute_time': "{:.2f}".format(process_time),
    }

    # return req
