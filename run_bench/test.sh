# sync; echo 1 | sudo tee /proc/sys/vm/drop_caches
# sleep 2


# pidIgnore=$(pidof python3)
# pidIgnore=$(echo "$pidIgnore" | tr ' ' ',')
# echo $pidIgnore

run_workload_in_faas() 
{
    curl http://127.0.0.1:8080/function/matmul-cxl -d '{"n":"15000"}' & sleep 2
    check_pid=$(pidof python3)
    if [[ -z $check_pid ]]; then
        echo "error getting sudo pid, pls run again!" && sudo pkill -9 python3 && exit 1
    fi
}

run_workload_in_bm() 
{
    # first evict so files
    # while IFS= read -r line
    # do 
    #     sudo vmtouch -e $line >> vmtouch_res.log 2>&1
    # done < "/home/cc/functions/run_bench/to_evict_bm.txt"
    # sudo numactl --cpunodebind 0 --membind 1 -- python3 /home/cc/functions/run_bench/normal_run/matmul.py 20000 & \
    numactl --cpunodebind 0 --membind 1 -- python2.7 /home/cc/functions/run_bench/normal_run/matmul.py 12000 & \
    check_pid=$!
    sleep 2
    if [[ -z $check_pid ]]; then
        echo "error getting sudo pid, pls run again!" && sudo pkill -9 python3 && exit 1
    fi
}

dump_logs()
{
    local workload_pid=$1
    local time=$2
    local env=$3
    # while IFS= read -r line
    # do
        # do vmtouch -e $line 
        # >> evict_res.log 2>&1; 
    sudo cat /proc/$workload_pid/numa_maps > numa_dstb_res_27/evict_res_numamaps_$time.txt
    # done < "/home/cc/functions/run_bench/to_evict_bm.txt"
} 

# $1: env <faas/bm>
if [[ $1 == "faas" ]]; then
    echo "running in faas"
    run_workload_in_faas
elif [[ $1 == "bm" ]]; then
    echo "running in baremetal"
    run_workload_in_bm
fi

i=0
while [ -d "/proc/${check_pid}" ]
do 

    echo "dumping to log $i"
    # echo "sudo pid $check_pid"
    # if [[ $1 == "bm" ]]; then
        # workload_pid=$(pgrep -P $check_pid)
        # echo "workload pid $workload_pid"
    dump_logs $check_pid $i $1 &
    # elif [[ $1 == "faas" ]]; then
    # dump_logs $check_pid $i $1 &
    # else
        # echo "argv[1]: env <faas/bm> " && exit 1
    # fi
    ((i=i+1))
    sleep 1
done
echo "finished"
