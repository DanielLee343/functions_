#!/bin/bash

PLAYGROUND_DIR=/home/cc/functions/run_bench/playground
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
TWITTER_BIG=/home/cc/functions/run_bench/normal_run/graph_dir/twitter_rv.el
TWITTER_WHOLE=/home/cc/gapbs/benchmark/twitter.sg
DAMO=/home/cc/damo/damo
# DAMO=damo
check_pid=99999
gen_rss() 
{
    local check_pid=$1
    local workload_name=$2
    # local do_graph=$3
    RSS_FILE=$PLAYGROUND_DIR/$workload_name/"$workload_name"_rss.csv
    rm -rf $RSS_FILE
    # if [ "$do_graph" = true ]; then
    time=0
    # echo "start gen rss at "$(date)
    while [ -d "/proc/${check_pid}" ]
    do
        cur_rss=$(ps aux | grep $check_pid | awk '{print $6}' | head -n 1 | awk '{print $1/1024}' | bc)
        time=$(echo "$time + 0.1" | bc)
        echo $time","$cur_rss >> $RSS_FILE
        sleep 0.1
    done
    # echo "finish gen rss at "$(date)
    # fi
    # TODO: plot rss
    gnuplot -e "output_file='$PLAYGROUND_DIR/$workload_name/"$workload_name"_rss.png'; \
        input_file='$RSS_FILE'; \
        wl_title='$workload_name'" \
        $SCRIPT_DIR/plot_rss.gnuplot 
    echo "plot rss done"
}

gen_bw()
{
    local check_pid=$1
    local workload_name=$2 
    BW_PCM_FILE=$PLAYGROUND_DIR/$workload_name/"$workload_name"_bw_raw.csv
    MEM_FP_FILE=$PLAYGROUND_DIR/$workload_name/"$workload_name"_numa_fp.csv
    rm -rf $MEM_FP_FILE
    sudo pcm-memory 0.1 -csv=$BW_PCM_FILE -f -silent &
    while [ -d "/proc/${check_pid}" ]
    do
        numactl -H | grep free >> $MEM_FP_FILE
        sleep 0.1
    done
    sudo pkill -9 pcm-memory >/dev/null 2>&1
    sleep 1

    python /home/cc/functions/run_bench/process_numa_mem.py $MEM_FP_FILE $func fp
    python /home/cc/functions/run_bench/process_numa_mem.py $BW_PCM_FILE $workload_name bw
    gnuplot -e "output_file='$PLAYGROUND_DIR/$workload_name/"$workload_name"_bw.png'; \
        input_file='$PLAYGROUND_DIR/$workload_name/"$workload_name"_bw.csv'; \
        wl_title='$workload_name'" \
        $SCRIPT_DIR/plot_bw.gnuplot 
    echo "plot bw done"
    python /home/cc/functions/run_bench/get_bw_wss_stat.py $workload_name bw
}

gen_heatmap()
{
    local check_pid=$1
    local workload_name=$2
    local do_run_damo=$3
    # check if region range is good
    DEMO_FILE=$PLAYGROUND_DIR/$workload_name/"$workload_name".data
    # DEMO_FILE=/home/cc/functions/run_bench/playground/gapbs_bc_twitter_whole/gapbs_bc_twitter_whole.data
    echo "DAMO_FILE: " $DEMO_FILE
    if [ "$do_run_damo" = true ]; then
        echo "running damo..."
        # sudo $DAMO record -s 1000 -a 100000 -u 1000000 -n 5000 -m 6000 \
        #     -o $DEMO_FILE $check_pid
        sudo $DAMO record -o $DEMO_FILE $check_pid
    fi
    echo "processig damo..."
    # sudo $DAMO report raw -i $DEMO_FILE \
    #     > $PLAYGROUND_DIR/$workload_name/"$workload_name".txt & # <- no need 
    # sudo $DAMO report heats -i $DEMO_FILE \
    #     --heatmap $PLAYGROUND_DIR/$workload_name/"$workload_name".png &
    # # sudo $DAMO report wss -i $DEMO_FILE \
    # #     --sortby time \
    # #     --range 0 100 1 \
    # #     --plot $PLAYGROUND_DIR/$workload_name/"$workload_name"_wss.png &
    # # sudo $DAMO report wss -i $DEMO_FILE \
    # #     --all_wss > $PLAYGROUND_DIR/$workload_name/"$workload_name"_wss.txt &
    # sudo $DAMO report heats -i $DEMO_FILE \
    #     --abs_addr > $PLAYGROUND_DIR/$workload_name/abs_addr.txt &
    # while [ ! -z "$(ps aux | grep 'damo' | grep -v grep | awk '{print $2}' | head -n 1)" ]
    # do
    #     sleep 1
    # done
    # sudo chown -R $(whoami) $PLAYGROUND_DIR/$workload_name/*
    # python /home/cc/functions/run_bench/get_bw_wss_stat.py $workload_name wss
    # echo "plot wss and heatmap done"
}
kill_remain_damo()
{
    perf_record_pid=$(ps aux | grep 'damo' | grep -v grep | awk '{print $2}' | head -n 1)
    if [ ! -z $perf_record_pid ]; then
        echo "killing remain damo $perf_record_pid"
        sudo kill -9 $perf_record_pid
    fi
}

wait_4_gen_rss()
{
    local func=$1
    local wl_folder=$2
    local check_pid=$3
    if [ "$func" = "pagerank" ] || [ "$func" = "mst" ] || [ "$func" = "bfs" ] || [ "$func" = "biconnect" ] \
    || [[ $func == "dl_"* ]] || [[ $func == "gapbs_"* ]]; then
        echo "waiting for damo to start1"
        while [ -z "$(ps aux | grep 'damo' | grep -v grep | awk '{print $2}' | head -n 1)" ]
        do
            sleep 0.1
        done
        echo "found damo, start gen_rss"
        gen_rss $check_pid $wl_folder &
    else
        gen_rss $check_pid $wl_folder &
    fi
}

wait_4_gen_bw()
{
    local func=$1
    local wl_folder=$2
    local check_pid=$3
    if [ "$func" = "pagerank" ] || [ "$func" = "mst" ] || [ "$func" = "bfs" ] || [ "$func" = "biconnect" ] \
    || [[ $func == "dl_"* ]] || [[ $func == "gapbs_"* ]]; then
        echo "waiting for damo to start2"
        while [ -z "$(ps aux | grep 'damo' | grep -v grep | awk '{print $2}' | head -n 1)" ]
        do
            sleep 0.1
        done
        echo "found damo, start gen_bw"
        gen_bw $check_pid $wl_folder &
    else
        gen_bw $check_pid $wl_folder &
    fi
}

wait_4_gen_heatmap()
{
    local func=$1
    local wl_folder=$2
    local check_pid=$3
    if [ "$func" = "pagerank" ] || [ "$func" = "mst" ] || [ "$func" = "bfs" ] || [ "$func" = "biconnect" ] \
    || [[ $func == "gapbs_"* ]] || [[ $func == "dl_"* ]]; then
        echo "waiting for worklaod to finish"
        # while [ -z "$(ps aux | grep 'damo' | grep -v grep | awk '{print $2}' | head -n 1)" ]
        # do
        #     echo "waiting for damo to start..."
        #     sleep 0.1
        # done
        # if running graph wl, damo runs inside workload script, so we wait till wl finishes
        while [ -d "/proc/${check_pid}" ]
        do
            # echo "damo, or wl still running..."
            sleep 0.5
        done
        sleep 4
        gen_heatmap $check_pid $wl_folder false &
    else
        gen_heatmap $check_pid $wl_folder true &
    fi
}

get_numa_mem_stat()
{
    echo "getting numa mem footprint stat"
    local func=$1
    local check_pid=$2
    MEM_FP_FILE=$PLAYGROUND_DIR/$func/"$func"_numa_fp.csv
    rm -rf $MEM_FP_FILE
    while [ -d "/proc/${check_pid}" ]
    do
        # echo "damo, or wl still running..."
        numactl -H | grep free >> $MEM_FP_FILE
        sleep 0.1
    done
    echo "numa stat done"
    sleep 1
    python /home/cc/functions/run_bench/process_numa_mem.py $MEM_FP_FILE $func fp
}

run_workload()
{
    # cxl, base
    local env=$1
    # which workload
    local func=$2
    # bm (bare metal), faas, add later
    local wl_args=$3

    get_rss=true
    get_bw=true
    get_heatmap=true
    run_vtune=false
    if [ ! -z $wl_args ]; then
        wl_folder="$func"_"$wl_args"
    else
        wl_folder=$func
    fi
    echo "folder name in playground:" $wl_folder

    echo "running $func in $env"
    if [ "$env" = "cxl" ]; then
        cmd_prefix="numactl --cpunodebind 0 --membind 1 -- "
    elif [ "$env" = "base" ]; then
        cmd_prefix="numactl --cpunodebind 0 --membind 0 -- "
    elif [ "$env" = "cpu0" ]; then
        cmd_prefix="numactl --cpunodebind 0 -- "
    elif [ "$env" = "interleave" ]; then
        cmd_prefix="numactl --cpunodebind 0 --interleave all -- "
    elif [ "$env" = "org" ]; then
        cmd_prefix=""
    else
        echo "wrong env, pls try again!"; exit 1
    fi
    
    if [ "$func" = "chameleon" ]; then
        workload_cmd="python /home/cc/functions/run_bench/normal_run/chameleon_.py 6000"
    elif [ "$func" = "para_comp" ]; then
        workload_cmd="python /home/cc/functions/run_bench/normal_run/para_comp.py 9000000000 12"
    elif [ "$func" = "img_proc" ]; then
        workload_cmd="python /home/cc/functions/run_bench/normal_run/img_proc/img_proc.py 191mb"
    elif [ "$func" = "img_recog" ]; then
        vmtouch -vt /home/cc/functions/run_bench/normal_run/img_recog/images >/dev/null 2>&1
        vmtouch -vt /home/cc/functions/run_bench/normal_run/img_recog/resnet50-19c8e357.pth >/dev/null 2>&1
        workload_cmd="python /home/cc/functions/run_bench/normal_run/img_recog/img_recog.py place_holder"
    elif [ "$func" = "matmul_go" ]; then
        workload_cmd="matmul 12000"
    elif [ "$func" = "linpack_go" ]; then
        workload_cmd="linpack 4000"
    elif [ "$func" = "pagerank" ]; then
        # local wl_args=$4
        workload_cmd="python /home/cc/functions/run_bench/normal_run/graph_.py pagerank $wl_args $run_vtune $get_heatmap"
    elif [ "$func" = "bfs" ]; then
        # local wl_args=$4
        workload_cmd="python /home/cc/functions/run_bench/normal_run/graph_.py bfs $wl_args $run_vtune $get_heatmap"
    elif [ "$func" = "mst" ]; then
        # local wl_args=$4
        workload_cmd="python /home/cc/functions/run_bench/normal_run/graph_.py mst $wl_args $run_vtune $get_heatmap"
    # elif [ "$func" = "clusters" ]; then
        # local wl_args=$4
        # workload_cmd="python /home/cc/functions/run_bench/normal_run/graph_.py clusters $wl_args"
    elif [ "$func" = "biconnect" ]; then
        # local wl_args=$4
        workload_cmd="python /home/cc/functions/run_bench/normal_run/graph_.py biconnect $wl_args $run_vtune $get_heatmap"
    elif [ "$func" = "gif" ]; then
        workload_cmd="python /home/cc/functions/run_bench/normal_run/watermark/watermark.py concat to_gif"
    elif [ "$func" = "watermark" ]; then
        workload_cmd="python /home/cc/functions/run_bench/normal_run/watermark/watermark.py 137_4k watermark"

    elif [ "$func" = "resnet18_train" ]; then
        workload_cmd="python /home/cc/bm_test/cifar100/cifar100.py train resnet18 50000"
    elif [ "$func" = "squeezenet_train" ]; then
        workload_cmd="python /home/cc/bm_test/cifar100/cifar100.py train squeezenet 50000"
    elif [ "$func" = "resnet152_train" ]; then
        workload_cmd="python /home/cc/bm_test/cifar100/cifar100.py train resnet152 6000" 
    elif [ "$func" = "vgg16_train" ]; then
        workload_cmd="python /home/cc/bm_test/cifar100/cifar100.py train vgg16 50000"
    elif [ "$func" = "attention56_train" ]; then
        workload_cmd="python /home/cc/bm_test/cifar100/cifar100.py train attention56 40000"
    elif [ "$func" = "resnet152_serve" ]; then
        workload_cmd="python /home/cc/bm_test/cifar100/cifar100.py serve resnet152 10000"
    elif [ "$func" = "inceptionv4_serve" ]; then
        workload_cmd="python /home/cc/bm_test/cifar100/cifar100.py serve inceptionv4 10000"
    elif [ "$func" = "resnet50_serve" ]; then
        workload_cmd="python /home/cc/bm_test/cifar100/cifar100.py serve resnet50 10000"
    elif [ "$func" = "squeezenet_serve" ]; then
        workload_cmd="python /home/cc/bm_test/cifar100/cifar100.py serve squeezenet 10000"
    elif [ "$func" = "vgg16_serve" ]; then
        workload_cmd="python /home/cc/bm_test/cifar100/cifar100.py serve vgg16 10000"

    elif [ "$func" = "dl_cifar100_resnet50_128" ]; then
        vmtouch -vt /home/cc/functions/dl/cifar100 >/dev/null 2>&1
        vmtouch -vt /home/cc/functions/dl/resnet50 >/dev/null 2>&1
        workload_cmd="python /home/cc/functions/dl/dl.py -job dl -e 1 -d cifar100 -m resnet50 -b 128 -hm"
    elif [ "$func" = "dl_cifar100_resnet50_32" ]; then
        vmtouch -vt /home/cc/functions/dl/cifar100 >/dev/null 2>&1
        vmtouch -vt /home/cc/functions/dl/resnet50 >/dev/null 2>&1
        workload_cmd="python /home/cc/functions/dl/dl.py -job dl -e 1 -d cifar100 -m resnet50 -b 32 -hm"
    elif [ "$func" = "dl_cifar100_resnet152_128" ]; then
        vmtouch -vt /home/cc/functions/dl/cifar100 >/dev/null 2>&1
        vmtouch -vt /home/cc/functions/dl/resnet152 >/dev/null 2>&1
        workload_cmd="python /home/cc/functions/dl/dl.py -job dl -e 1 -d cifar100 -m resnet152 -b 128 -hm"
    elif [ "$func" = "dl_cifar10_mobilenet_128" ]; then
        vmtouch -vt /home/cc/functions/dl/cifar10 >/dev/null 2>&1
        vmtouch -vt /home/cc/functions/dl/mobilenet >/dev/null 2>&1
        workload_cmd="python /home/cc/functions/dl/dl.py -job dl -e 5 -d cifar10 -m mobilenet -b 128 -hm"
    elif [ "$func" = "dl_downsample_imagenet_resnet50_128" ]; then
        vmtouch -vt /home/cc/functions/dl/train_data_batch_1 >/dev/null 2>&1
        vmtouch -vt /home/cc/functions/dl/resnet50_imagenet >/dev/null 2>&1
        workload_cmd="python /home/cc/functions/dl/dl.py -job dl -e 1 -d downsample_imagenet -m resnet50 -b 128 -hm"
    elif [ "$func" = "dl_downsample_imagenet_resnet50_512" ]; then
        vmtouch -vt /home/cc/functions/dl/train_data_batch_1 >/dev/null 2>&1
        vmtouch -vt /home/cc/functions/dl/resnet50_imagenet >/dev/null 2>&1
        workload_cmd="python /home/cc/functions/dl/dl.py -job dl -e 1 -d downsample_imagenet -m resnet50 -b 512 -hm"
    elif [ "$func" = "dl_inference" ]; then
        workload_cmd="python /home/cc/functions/dl/inference.py 16 true"

    elif [ "$func" = "gapbs_bc_twitter_whole" ]; then
        cd ~/gapbs
        make
        cd 
        workload_cmd="/home/cc/gapbs/bc -f $TWITTER_WHOLE -i4 -n4 -d $func"
    elif [ "$func" = "gapbs_bfs_23" ]; then
        cd ~/gapbs
        make
        cd
        workload_cmd="/home/cc/gapbs/bfs -g 23 -n 1000 -d $func"
    elif [ "$func" = "gapbs_bfs_twitter_whole" ]; then
        cd ~/gapbs
        make
        cd
        workload_cmd="/home/cc/gapbs/bfs -f $TWITTER_WHOLE -n 150 -d $func"
    elif [ "$func" = "gapbs_cc_twitter_whole" ]; then
        cd ~/gapbs
        make
        cd
        workload_cmd="/home/cc/gapbs/cc -f $TWITTER_WHOLE -n64 -d $func"
    elif [ "$func" = "gapbs_tc_twitter_whole" ]; then
        cd ~/gapbs
        make
        cd
        workload_cmd="/home/cc/gapbs/tc -f $TWITTER_WHOLE -n3 -d $func"
    elif [ "$func" = "gapbs_pr_twitter_whole" ]; then
        cd ~/gapbs
        make
        cd
        workload_cmd="/home/cc/gapbs/pr -f $TWITTER_WHOLE -i1000 -t1e-4 -n2 -d $func"
    else
        echo "wrong workload"; exit 1
    fi
    echo "playground: " $PLAYGROUND_DIR/$wl_folder
    if [ ! -d "$PLAYGROUND_DIR/$wl_folder" ]; then
        echo "creating folder" $PLAYGROUND_DIR/$wl_folder
        mkdir -p $PLAYGROUND_DIR/$wl_folder
    # else
        # echo "deleting everything inside folders" $PLAYGROUND_DIR/$wl_folder/*
        # rm -rf $PLAYGROUND_DIR/$wl_folder/*
    fi
    # echo "check now!!"
    # sleep 20
    # delete & if doing vtune, otherwise vtune doesn't know when to stop
    # export LD_PRELOAD=/home/cc/syscall_intercept/test/porter_lib.so
    export LD_PRELOAD=/home/cc/syscall_intercept/test/static_placement.so
    if [[ $func == "gapbs_"* ]]; then
        export OMP_NUM_THREADS=8
    fi
    # run workload
    # 2> $PLAYGROUND_DIR/$wl_folder/intercepted.log
    $cmd_prefix $workload_cmd 2> $PLAYGROUND_DIR/$wl_folder/intercepted_095rand.log &
    check_pid=$!
    if [ "$check_pid" = "" ]; then
        echo "unable to get wl pid, something is wrong"; exit 1
    fi
    unset LD_PRELOAD
    # if [ "$run_vtune" = true ] ; then
    #     if [ "$func" = "pagerank" ] || [ "$func" = "mst" ] || [ "$func" = "bfs" ] || [ "$func" = "biconnect" ]; then
    #         vtune_pid=$(ps aux | grep 'damo' | grep -v grep | awk '{print $2}' | head -n 1)
    #         while [ ! -z "" ]; then
    #             echo "killing $perf_record_pid"
    #             sudo kill -9 $perf_record_pid
    #         fi
    #     fi
    # fi

    # run_trace_prefix="numactl --cpunodebind 1 -- "
    # get_numa_mem_stat $wl_folder $check_pid &
    if [ "$get_rss" = true ] ; then
        wait_4_gen_rss $func $wl_folder $check_pid &

    fi
    if [ "$get_bw" = true ]; then
        wait_4_gen_bw $func $wl_folder $check_pid &
    fi
    if [ "$get_heatmap" = true ]; then
        wait_4_gen_heatmap $func $wl_folder $check_pid
    fi
    echo "returning"
    return $check_pid
}

# $1: env <base, cxl>
# $2: function to run <chameleon>
echo 1 | sudo tee /proc/sys/vm/drop_caches
# funcs=("chameleon" "para_comp" "img_proc" "matmul_go" "linpack_go" "gif" "watermark" "dl_cifar100_resnet50_128" \
#         "dl_cifar100_resnet50_32" "dl_cifar100_resnet152_128" "dl_cifar10_mobilenet_128" "dl_downsample_imagenet_resnet50_128")
# funcs=("gapbs_bfs_23")
# envs=("cxl")

# for fn in "${funcs[@]}"
# do
#     for env in "${envs[@]}"
#     do
#         echo 1 | sudo tee /proc/sys/vm/drop_caches
#         echo running $fn in $env 
#         pid=$(run_workload $env $fn > /home/cc/functions/run_bench/logs/"$fn"_"$env".log)
#         echo "pid: " $pid
#         while [ -d "/proc/${check_pid}" ]
#         do
#             sleep 1
#         done
#         sleep 5
#     done
# done
sudo pkill -9 python
kill_remain_damo
run_workload $1 $2 $3
