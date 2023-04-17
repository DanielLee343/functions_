#!/bin/bash
wls=("chameleon" "para_comp" "img_proc" "matmul_go" "linpack_go" "pagerank" "bfs" "mst" "gif" "watermark" "resnet18_train" "squeezenet_train" "resnet152_serve")
test=("para_comp")
for wl in "${wls[@]}"
do
    echo doing $wl ...
    output_file=./playground/"$wl"/"$wl"_wss.txt
    # sudo damo report wss -i ./playground/$wl/$wl.data --all_wss > $output_file
    python /home/cc/functions/run_bench/get_bw_wss_stat.py $wl wss
done