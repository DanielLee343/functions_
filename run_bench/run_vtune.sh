#!/bin/bash

PLAYGROUND_DIR=/home/cc/functions/run_bench/playground
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
gen_rss() 
{
    local check_pid=$1
    local workload_name=$2
    # local do_graph=$3
    RSS_FILE=$PLAYGROUND_DIR/$workload_name/"$workload_name"_rss.csv

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

gen_heatmap()
{
    local check_pid=$1
    local workload_name=$2
    local do_run_damo=$3
    # check if region range is good
    DEMO_FILE=$PLAYGROUND_DIR/$workload_name/"$workload_name".data
    if [ "$do_run_damo" = true ]; then
        sudo damo record --monitoring_nr_regions_range 1000 2000 \
            -o $DEMO_FILE $check_pid
    fi
    echo "processig damo..."
    sudo damo report raw -i $DEMO_FILE \
        > $PLAYGROUND_DIR/$workload_name/"$workload_name".txt
    sudo damo report heats -i $DEMO_FILE \
        --heatmap $PLAYGROUND_DIR/$workload_name/"$workload_name".png
    sudo damo report wss -i $DEMO_FILE \
        --all_wss > $PLAYGROUND_DIR/$workload_name/"$workload_name"_wss.txt
    sudo damo report wss -i $DEMO_FILE \
        --sortby time \
        --range 0 100 1 \
        --plot $PLAYGROUND_DIR/$workload_name/"$workload_name"_wss.png
    sudo chown -R $(whoami) $PLAYGROUND_DIR/$workload_name/*
    python /home/cc/functions/run_bench/get_bw_wss_stat.py $workload_name wss
    echo "plot wss and heatmap done"
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
    run_vtune=true
    if [ ! -z $wl_args ]; then
        wl_folder="$func"_"$wl_args"
    else
        wl_folder=$func
    fi
    echo "folder name in playground:" $wl_folder

    if [ ! -d "$PLAYGROUND_DIR/$wl_folder" ]; then
        # echo "does not exists"
        mkdir -p $PLAYGROUND_DIR/$wl_folder
    else
        rm -rf $PLAYGROUND_DIR/$wl_folder/*
    fi
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
        workload_cmd="python /home/cc/functions/run_bench/normal_run/chameleon_.py 6000"
    elif [ "$func" = "para_comp" ]; then
        workload_cmd="python /home/cc/functions/run_bench/normal_run/para_comp.py 9000000000 12"
    elif [ "$func" = "img_proc" ]; then
        workload_cmd="python /home/cc/functions/run_bench/normal_run/img_proc/img_proc.py 191mb"
    elif [ "$func" = "matmul_go" ]; then
        workload_cmd="matmul 13000"
    elif [ "$func" = "linpack_go" ]; then
        workload_cmd="linpack 7000"
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

    # elif [ "$func" = "reddit_5k" ]; then
    #     workload_cmd="python /home/cc/tudataset/tud_benchmark/unit_test.py REDDIT-MULTI-5K"
    # elif [ "$func" = "FRANKENSTEIN" ]; then
    #     workload_cmd="python /home/cc/tudataset/tud_benchmark/unit_test.py FRANKENSTEIN"
    # elif [ "$func" = "COLLAB" ]; then
    #     workload_cmd="python /home/cc/tudataset/tud_benchmark/unit_test.py COLLAB"
    # elif [ "$func" = "Fingerprint" ]; then
    #     workload_cmd="python /home/cc/tudataset/tud_benchmark/unit_test.py Fingerprint"
    # elif [ "$func" = "NCI1" ]; then
    #     workload_cmd="python /home/cc/tudataset/tud_benchmark/unit_test.py NCI1"
    # elif [ "$func" = "DD" ]; then
    #     workload_cmd="python /home/cc/tudataset/tud_benchmark/unit_test.py DD"
    else
        echo "wrong workload"; exit 1
    fi
    # delete & if doing vtune, otherwise vtune doesn't know when to stop
    $cmd_prefix $workload_cmd &
    check_pid=$!
    if [ "$check_pid" = "" ]; then
        echo "unable to get wl pid, something is wrong"; exit 1
    fi
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
    if [ "$get_rss" = true ] ; then
        if [ "$func" = "pagerank" ] || [ "$func" = "mst" ] || [ "$func" = "bfs" ] || [ "$func" = "biconnect" ]; then
            perf_record_pid=$(ps aux | grep 'damo' | grep -v grep | awk '{print $2}' | head -n 1)
            if [ ! -z $perf_record_pid ]; then
                echo "killing $perf_record_pid"
                sudo kill -9 $perf_record_pid
            fi
            while [ -z "$(ps aux | grep 'damo' | grep -v grep | awk '{print $2}' | head -n 1)" ]
            do
                sleep 0.1
            done
            echo "found damo, start gen_rss"
            gen_rss $check_pid $wl_folder &
        else
            gen_rss $check_pid $wl_folder &
        fi
    fi
    if [ "$get_bw" = true ]; then
        if [ "$func" = "pagerank" ] || [ "$func" = "mst" ] || [ "$func" = "bfs" ]; then
            while [ -z "$(ps aux | grep 'damo' | grep -v grep | awk '{print $2}' | head -n 1)" ]
            do
                sleep 0.1
            done
            echo "found damo, start gen_bw"
            gen_bw $check_pid $wl_folder &
        else
            gen_bw $check_pid $wl_folder &
        fi
    fi
    if [ "$get_heatmap" = true ]; then
        if [ "$func" = "pagerank" ] || [ "$func" = "mst" ] || [ "$func" = "bfs" ] || [ "$func" = "biconnect" ]; then
            # while [ -z "$(ps aux | grep 'damo' | grep -v grep | awk '{print $2}' | head -n 1)" ]
            # do
            #     echo "waiting for damo to start..."
            #     sleep 0.1
            # done
            # if running graph wl, damo runs inside workload script, so we wait till wl finishes
            while [ -d "/proc/${check_pid}" ]
            do
                # echo "damo, or wl still running..."
                sleep 0.1
            done
            sleep 3
            gen_heatmap $check_pid $wl_folder false &
        else
            gen_heatmap $check_pid $wl_folder true &
        fi
    fi
}

# $1: env <base, cxl>
# $2: function to run <chameleon>
echo 1 | sudo tee /proc/sys/vm/drop_caches
run_workload $1 $2 $3