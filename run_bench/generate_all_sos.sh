# !/bin/bash

numactl --cpunodebind 0 --membind 1 -- python /home/cc/functions/run_bench/normal_run/matmul.py 10000 & 
# curl http://127.0.0.1:8080/function/matmul-cxl -d '{"n":"10000"}' & 
check_pid=$!
sleep 2
# workload_pid=$(pgrep -P $check_pid)

# workload_pid=$(pidof python3)
if [[ -z $check_pid ]]; then
    echo "failed to obtain workload pid, pls try again" && sudo pkill -9 python3 && exit 1
fi

i=0
while [ -d "/proc/${check_pid}" ]
do 
    echo "dumping to log $i"
    # echo "sudo pid $workload_pid"
    # workload_pid=$(pgrep -P $workload_pid)
    # echo "workload pid $workload_pid"
    sudo lsof -p $check_pid > python3_sos/log_from_lsof_$i.txt &
    ((i=i+1))
    sleep 1
done
echo "finished!"
