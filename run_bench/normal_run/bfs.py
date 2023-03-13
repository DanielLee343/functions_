import datetime
import igraph

def main():

    size = 10

    graph_generating_begin = datetime.datetime.now()
    graph = igraph.Graph.Barabasi(size, 10)
    graph_generating_end = datetime.datetime.now()

    process_begin = datetime.datetime.now()
    result = graph.bfs(0)
    process_end = datetime.datetime.now()

    graph_generating_time = (graph_generating_end - graph_generating_begin) / datetime.timedelta(microseconds=1)
    process_time = (process_end - process_begin) / datetime.timedelta(microseconds=1)
    print(result)
    print(graph_generating_time)
    print(process_time)

    return {
            'result': result,
            'measurement': {
                'graph_generating_time': graph_generating_time,
                'compute_time': process_time
            }
    }

main()