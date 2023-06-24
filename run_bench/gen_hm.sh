#!/bin/bash
# DAMO=damo
DAMO=/home/cc/damo/damo
PLAYGROUND_DIR=/home/cc/functions/run_bench/playground
gen_heatmap()
{
    local workload_name=$1
    # check if region range is good
    DEMO_FILE=$PLAYGROUND_DIR/$workload_name/"$workload_name".data
    # DEMO_FILE=/home/cc/functions/run_bench/playground/gapbs_bc_twitter_whole/gapbs_bc_twitter_whole.data
    echo "DAMO_FILE: " $DEMO_FILE
    echo "processig damo..."

    if [ ! -e "$DEMO_FILE" ]; then
        echo "File does not exist"; exit 1
    fi

    # sudo $DAMO report raw -i $DEMO_FILE \
    #     > $PLAYGROUND_DIR/$workload_name/"$workload_name".txt & # <- no need 
    # sudo numactl --cpunodebind 1 -- $DAMO report wss -i $DEMO_FILE \
    #     --sortby time \
    #     --range 0 100 1 \
    #     --plot $PLAYGROUND_DIR/$workload_name/"$workload_name"_wss.png &
    # sudo numactl --cpunodebind 1 -- $DAMO report wss -i $DEMO_FILE \
    #     --all_wss > $PLAYGROUND_DIR/$workload_name/"$workload_name"_wss.txt &
    sudo $DAMO report heats -i $DEMO_FILE --guide &
    sudo $DAMO report heats -i $DEMO_FILE \
        --resol 1000 2000 --heatmap $PLAYGROUND_DIR/$workload_name/"$workload_name".png &
    sudo $DAMO report heats -i $DEMO_FILE \
        --abs_time --abs_addr --resol 1000 2000 > $PLAYGROUND_DIR/$workload_name/abs_addr_time.txt &

    while [ ! -z "$(ps aux | grep 'damo' | grep -v grep | awk '{print $2}' | head -n 1)" ]
    do
        sleep 1
    done
    sudo chown -R $(whoami) $PLAYGROUND_DIR/$workload_name/*
    # python /home/cc/functions/run_bench/get_bw_wss_stat.py $workload_name wss
    # if [ "$workload_name" = "gif" ]; then
        # /home/cc/functions/run_bench/truncate_file.sh
    # python /home/cc/functions/run_bench/split_lines.py $workload_name
    # fi
    echo "plot wss and heatmap done"
}
gen_heatmap_time_range()
{
    local workload_name=$1
    local start_time=$2
    local end_time=$3
    DEMO_FILE=$PLAYGROUND_DIR/$workload_name/"$workload_name".data
    echo "DAMO_FILE: " $DEMO_FILE
    echo "processig damo..."

    # sudo $DAMO report heats -i $DEMO_FILE \
    #     --guide > $PLAYGROUND_DIR/$workload_name/guide.txt
    # sudo $DAMO report heats -i $DEMO_FILE \
    #     --address_range 00000140722053316608 00000140735203876864 > $PLAYGROUND_DIR/$workload_name/address_range.txt
    sudo $DAMO report heats -i $DEMO_FILE --abs_time \
        --time_range 1012459133759960 1012475178539480 > $PLAYGROUND_DIR/$workload_name/real_compute_abs_time.txt
    # while [ ! -z "$(ps aux | grep 'damo' | grep -v grep | awk '{print $2}' | head -n 1)" ]
    # do
    #     sleep 1
    # done
    sudo chown -R $(whoami) $PLAYGROUND_DIR/$workload_name/*
    # python /home/cc/functions/run_bench/get_bw_wss_stat.py $workload_name wss
    echo "plot wss and heatmap done"
}

# $1: workload name, eg., dl_cifar100_resnet50_128
# gen_heatmap_time_range $1 $2 $3
gen_heatmap $1