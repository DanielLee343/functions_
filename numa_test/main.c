#include <numa.h>
#include <stdio.h>

int main() {
    long numa_num_task_nodes = numa_node_size(0, NULL);
    printf("%ld\n", numa_num_task_nodes);
    return 0;
}