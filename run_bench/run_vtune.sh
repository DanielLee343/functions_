#!/bin/bash

PLAYGROUND_DIR=/home/cc/functions/run_bench/playground
gen_rss() 
{
    local check_pid=$1
    local workload_name=$2
    RSS_FILE=$PLAYGROUND_DIR/$workload_name/"$workload_name"_rss.csv

    time=0
    while [ -d "/proc/${check_pid}" ]
    do
        cur_rss=$(ps aux | grep $check_pid | awk '{print $6}' | head -n 1 | awk '{print $1/1024}' | bc)
        time=$(echo "$time + 0.1" | bc)
        echo $time","$cur_rss >> $RSS_FILE
        sleep 0.1
    done
    # TODO: plot rss
    gnuplot -e "output_file='$PLAYGROUND_DIR/$workload_name/"$workload_name"_rss.png'; \
        input_file='$RSS_FILE'; \
        wl_title='$workload_name'" \
        ./plot_rss.gnuplot 
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
    echo "generating BW csv for $workload_name"
    python /home/cc/functions/run_bench/process_numa_mem.py $BW_PCM_FILE $workload_name
    # TODO: generate plot
    gnuplot -e "output_file='$PLAYGROUND_DIR/$workload_name/"$workload_name"_bw.png'; \
        input_file='$PLAYGROUND_DIR/$workload_name/"$workload_name"_bw.csv'; \
        wl_title='$workload_name'" \
        ./plot_bw.gnuplot 
    echo "done"
}

gen_heatmap()
{
    local check_pid=$1
    local workload_name=$2
    # check if region range is good
    DEMO_FILE=$PLAYGROUND_DIR/$workload_name/"$workload_name".data
    sudo damo record --monitoring_nr_regions_range 1000 2000 \
        -o $DEMO_FILE $check_pid
    sudo damo report raw -i $DEMO_FILE \
        > $PLAYGROUND_DIR/$workload_name/"$workload_name".txt
    sudo damo report heats -i $DEMO_FILE \
        --heatmap $PLAYGROUND_DIR/$workload_name/"$workload_name".png
    sudo damo report wss -i $DEMO_FILE \
        --sortby time \
        --range 0 100 1 \
        --plot $PLAYGROUND_DIR/$workload_name/"$workload_name"_wss.png
    sudo chown -R $(whoami) $PLAYGROUND_DIR/$workload_name/*
}

run_workload()
{
    # cxl, base
    local env=$1
    # which workload
    local func=$2
    # bm (bare metal), faas, add later
    local level=$3

    get_rss=true
    get_bw=false
    get_heatmap=false

    echo "running $func in $env"
    if [ "$env" = "cxl" ]; then
        cmd_prefix="numactl --cpunodebind 0 --membind 1 -- "
    elif [ "$env" = "base" ]; then
        cmd_prefix="numactl --cpunodebind 0 --membind 0 -- "
    elif [ "$env" = "org" ]; then
        cmd_prefix=""
    else
        echo "wrong env, pls try again!"; exit 1
    fi
    
    if [ "$func" = "chameleon" ]; then
        workload_cmd="python /home/cc/functions/run_bench/normal_run/chameleon_.py 1500"
    elif [ "$func" = "para_comp" ]; then
        workload_cmd="python /home/cc/functions/run_bench/normal_run/para_comp.py 3000000000 12"
    elif [ "$func" = "img_proc" ]; then
        workload_cmd="python /home/cc/functions/run_bench/normal_run/img_proc/img_proc.py 63mb"
    elif [ "$func" = "matmul_go" ]; then
        workload_cmd="matmul 7000"
    elif [ "$func" = "linpack_go" ]; then
        workload_cmd="linpack 3000"
    elif [ "$func" = "pagerank" ]; then
        workload_cmd="python /home/cc/functions/run_bench/normal_run/graph.py pagerank 4000000"
    elif [ "$func" = "bfs" ]; then
        workload_cmd="python /home/cc/functions/run_bench/normal_run/graph.py bfs 4000000"
    elif [ "$func" = "mst" ]; then
        workload_cmd="python /home/cc/functions/run_bench/normal_run/graph.py mst 4000000"
    elif [ "$func" = "gif" ]; then
        workload_cmd="python /home/cc/functions/run_bench/normal_run/watermark/watermark.py 30mb to_gif"
    elif [ "$func" = "watermark" ]; then
        workload_cmd="python /home/cc/functions/run_bench/normal_run/watermark/watermark.py 78_4k watermark"
    elif [ "$func" = "resnet18_train" ]; then
        workload_cmd="python /home/cc/bm_test/cifar100/cifar100.py train resnet18 6000"
    elif [ "$func" = "squeezenet_train" ]; then
        workload_cmd="python /home/cc/bm_test/cifar100/cifar100.py train squeezenet 10000"
    elif [ "$func" = "resnet152_serve" ]; then
        workload_cmd="python /home/cc/bm_test/cifar100/cifar100.py serve resnet152 4000"
    else
        echo "wrong workload"; exit 1
    fi

    $cmd_prefix $workload_cmd & 
    check_pid=$!
    if [ "$check_pid" = "" ]; then
        echo "unable to get wl pid, something is wrong"; exit 1
    fi

    if [ ! -d "$PLAYGROUND_DIR/$func" ]; then
        echo "does not exists"
        mkdir -p $PLAYGROUND_DIR/$func
    else
        rm -rf $PLAYGROUND_DIR/$func/*
    fi

    if [ "$get_rss" = true ] ; then
        gen_rss $check_pid $func &
    fi
    if [ "$get_bw" = true ]; then
        gen_bw $check_pid $func &
    fi
    if [ "$get_heatmap" = true ]; then
        gen_heatmap $check_pid $func &
    fi
}

# $1: env <base, cxl>
# $2: function to run <chameleon>
echo 1 | sudo tee /proc/sys/vm/drop_caches
run_workload $1 $2