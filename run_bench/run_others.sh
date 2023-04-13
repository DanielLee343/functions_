#!/bin/bash

# /home/cc/functions/run_bench/run_vtune.sh base matmul_go &
# python /home/cc/bm_test/cifar100/cifar100.py train squeezenet 10000 & 
# python /home/cc/functions/run_bench/normal_run/graph.py mst 1000000 &
sleep 3 &
check_pid=$!
sudo damo record --monitoring_nr_regions_range 1000 2000 -o /home/cc/functions/run_bench/playground/sleep.data $check_pid
# sudo chown -R cc ./playground/squeezenet_train.data

run_workload()
{

}
# $1: env <base, cxl>
# $2: function to run <chameleon>
echo 1 | sudo tee /proc/sys/vm/drop_caches
run_workload $1 $2
