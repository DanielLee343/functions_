#!/bin/bash

# /home/cc/functions/run_bench/run_vtune.sh base matmul_go &
# python /home/cc/bm_test/cifar100/cifar100.py train squeezenet 10000 & 
# python /home/cc/functions/run_bench/normal_run/graph.py mst 1000000 &
# sleep 3 &
# check_pid=$!
# sudo damo record --monitoring_nr_regions_range 1000 2000 -o /home/cc/functions/run_bench/playground/sleep.data $check_pid
# sudo chown -R cc ./playground/squeezenet_train.data

TWITTER_WHOLE=/home/cc/gapbs/benchmark/twitter.sg

run_interfer()
{
    local env=$1
    local func=$2
    local num_colocation=$3
    # local dl_train_cmd="python /home/cc/functions/dl/dl.py -job dl -e 1 -d cifar100 -m resnet50 -b 128"
    local func_cmd="python /home/cc/functions/dl/dl.py -job dl -e 1 -d downsample_imagenet -m resnet50 -b 128"

    echo "running $func in $env"
    if [ "$env" = "cxl" ]; then
        cmd_prefix_mem="--membind 1"
    elif [ "$env" = "base" ]; then
        cmd_prefix_mem="--membind 0"
    elif [ "$env" = "interleave" ]; then
        cmd_prefix_mem="--interleave all"
    else
        echo "wrong env, pls try again!"; exit 1
    fi
    if [ "$func" = "bfs" ]; then
        func_cmd="/home/cc/gapbs/bfs -f $TWITTER_WHOLE -n 20"
    elif [ "$func" = "inference" ]; then
        func_cmd="python /home/cc/functions/dl/inference.py 5"
    elif [ "$func" = "imagenet" ]; then
        func_cmd="python /home/cc/functions/dl/dl.py -job dl -e 1 -d downsample_imagenet -m resnet50 -b 128"
    elif [ "$func" = "cifar100" ]; then
        func_cmd="python /home/cc/functions/dl/dl.py -job dl -e 1 -d cifar100 -m resnet50 -b 128"
    else
         echo "wrong wl, pls try again!"; exit 1
    fi

    if [ "$num_colocation" = "1" ]; then
        numactl $cmd_prefix_mem --physcpubind 0 -- $func_cmd > /home/cc/functions/run_bench/interference/"$func"_standalone.log
    else
        half_num_func=$((num_colocation / 2))
        first_half_cpus=""
        second_half_cpus=""
        for ((i=0; i<half_num_func; i++))
        do
            # Append the formatted value to the variable
            first_half_cpus+="$((i*2)),"
        done
        last_cpu_A=$((half_num_func*2))
        for ((i=0; i<half_num_func; i++))
        do
            second_half_cpus+="$((last_cpu_A+i*2)),"
        done
        first_half_cpus=${first_half_cpus::-1}
        second_half_cpus=${second_half_cpus::-1}

        IFS=','
        for cpu in $first_half_cpus
        do
            echo "running first half on cpu: " $cpu
            # python /home/cc/functions/dl/dl.py -job dl -e 1 -d cifar100 -m resnet50 -b 128
            # /home/cc/gapbs/bfs -g 22 -n 280
            numactl --membind 1 --physcpubind $cpu -- python /home/cc/functions/dl/dl.py -job dl -e 1 -d cifar100 -m resnet50 -b 128 \
                > /home/cc/functions/run_bench/interference/"$func"_"$cpu".log &
        done
        # sleep 12
        for cpu in $second_half_cpus
        do
            echo "running second half on cpu: " $cpu 
            # /home/cc/gapbs/bfs -f $TWITTER_WHOLE -n 20
            numactl --membind 1 --physcpubind $cpu -- python /home/cc/functions/dl/dl.py -job dl -e 1 -d cifar100 -m resnet50 -b 128 \
                > /home/cc/functions/run_bench/interference/"$func"_"$cpu".log &
        done
    fi
}

gen_bw()
{
    local check_pid=$1
    local workload_name=$2 
    BW_PCM_FILE=$PLAYGROUND_DIR/$workload_name/"$workload_name"_bw_raw.csv
    sudo pcm-memory 0.1 -csv=$BW_PCM_FILE -f -silent &
    while [ -d "/proc/${check_pid}" ]
    do
        sleep 0.5
    done
    sudo pkill -9 pcm-memory >/dev/null 2>&1
    sleep 1

    # TODO: process the csv using python 
    python /home/cc/functions/run_bench/process_numa_mem.py $BW_PCM_FILE $workload_name
    # TODO: generate plot
    gnuplot -e "output_file='$PLAYGROUND_DIR/$workload_name/"$workload_name"_bw.png'; \
        input_file='$PLAYGROUND_DIR/$workload_name/"$workload_name"_bw.csv'; \
        wl_title='$workload_name'" \
        $SCRIPT_DIR/plot_bw.gnuplot 
    echo "plot bw done"
    python /home/cc/functions/run_bench/get_bw_wss_stat.py $workload_name bw
}

run_test()
{
    local env=$1
    if [ "$env" = "cxl" ]; then
        cmd_prefix_mem="--membind 1"
    elif [ "$env" = "base" ]; then
        cmd_prefix_mem="--membind 0"
    elif [ "$env" = "interleave" ]; then
        cmd_prefix_mem="--interleave all"
    else
        echo "wrong env, pls try again!"; exit 1
    fi
    numactl $cmd_prefix_mem --physcpubind 0,2,4 -- python /home/cc/functions/dl/dl.py -job dl -e 1 -d cifar100 -m resnet50 -b 128 \
                > /home/cc/functions/run_bench/interference/1_"$env".log &
    numactl $cmd_prefix_mem --physcpubind 6,8,10 -- python /home/cc/functions/dl/dl.py -job dl -e 1 -d cifar100 -m resnet50 -b 128 \
                > /home/cc/functions/run_bench/interference/2_"$env".log &
    numactl $cmd_prefix_mem --physcpubind 12,14,16 -- python /home/cc/functions/dl/dl.py -job dl -e 1 -d cifar100 -m resnet50 -b 128 \
                > /home/cc/functions/run_bench/interference/3_"$env".log &
    # numactl $cmd_prefix_mem --physcpubind 6 -- python /home/cc/functions/dl/dl.py -job dl -e 1 -d cifar100 -m resnet50 -b 128 \
    #             > /home/cc/functions/run_bench/interference/4_"$env".log &
    # numactl $cmd_prefix_mem --physcpubind 8 -- python /home/cc/functions/dl/dl.py -job dl -e 1 -d cifar100 -m resnet50 -b 128 \
    #             > /home/cc/functions/run_bench/interference/4_"$env".log &
    # numactl $cmd_prefix_mem --physcpubind 10 -- python /home/cc/functions/dl/dl.py -job dl -e 1 -d cifar100 -m resnet50 -b 128 \
    #             > /home/cc/functions/run_bench/interference/4_"$env".log &
    # numactl $cmd_prefix_mem --physcpubind 12,14,16 -- python /home/cc/functions/dl/dl.py -job dl -e 1 -d cifar100 -m resnet50 -b 128 \
    #             > /home/cc/functions/run_bench/interference/3_"$env".log &
    # numactl $cmd_prefix_mem --physcpubind 18,20,22 -- python /home/cc/functions/dl/dl.py -job dl -e 1 -d cifar100 -m resnet50 -b 128 \
    #             > /home/cc/functions/run_bench/interference/4_"$env".log &
}
# $1: env <base, cxl, interleave>
# $2: function to run <chameleon>
# $3: # colocation, 1: standalone
# e.g., /home/cc/functions/run_bench/run_intf.sh base bfs 4
echo 1 | sudo tee /proc/sys/vm/drop_caches
# export OMP_NUM_THREADS=12
# rm -rf /home/cc/functions/run_bench/interference/*
run_test $1
# run_interfer $1 $2 $3