#!/bin/bash

# $1: function to run

spin_single_func() 
{
    # $1: function to test <matmul, >
    # $2: parameter pass to function, e.g., matrix size

    # clear $1_$2.csv
    rm -r ./$1_$2.csv
    # get python pid to be ignored
    pidIgnore=$(pidof python3)
    pidIgnore=$(echo "$pidIgnore" | tr ' ' ',')
    # let the program run, wait for 0.05 sec for python to spin up
    cpus=""
    time curl http://127.0.0.1:8080/function/$1 -d '{"n":"'$2'"}' \
        & sleep 0.05

    pid=$(pidof python3 -o $pidIgnore)

    # get cpu ids involved, if needed
    # while :;
    # do
    #     check_pid=$(pidof python3 -o $pidIgnore)
    #     if [ -z "$check_pid" ]; then
    #         break
    #     else 
    #         cpus=$(echo $(taskset -cp $pid) | awk -F 'list: ' '{print $2}')
    #         echo $cpus
    #         sleep 1
    #     fi
    # done

    # use mpstat to get the CPU usage VS. time, if needed
    # mpstat -P ${cpus} 1

    # use pmap to get memory usage VS. time
    echo $pid
    while :;
    do
        check_pid=$(pidof python3 -o $pidIgnore)
        # if the function is finished
        if [ -z "$check_pid" ]; then
            break
        else 
            cur_rss=$(echo $(sudo pmap $pid -x | tail -n 1) | awk -F ' ' '{print $4}')
            now=$(date +"%T")
            echo $now","$(($cur_rss/1024)) >> $1_$2.csv
            sleep 1
        fi
    done
}

run_norm() 
{
    rm -r ./normal_run/$1_$2.csv
    pidIgnore=$(pidof python3)
    pidIgnore=$(echo "$pidIgnore" | tr ' ' ',')
    cpus=""
    time python3 ./normal_run/$1.py $2 \
        & sleep 0.05

    pid=$(pidof python3 -o $pidIgnore)

    # use pmap to get memory usage VS. time
    echo $pid
    while :;
    do
        check_pid=$(pidof python3 -o $pidIgnore)
        # if the function is finished
        if [ -z "$check_pid" ]; then
            break
        else 
            cur_rss=$(echo $(sudo pmap $pid -x | tail -n 1) | awk -F ' ' '{print $4}')
            now=$(date +"%T")
            echo $now","$(($cur_rss/1024)) >> ./normal_run/$1_$2.csv
            sleep 1
        fi
    done
}

get_func_cpu_usage() 
{
    pidIgnore=$(pidof python3)
    pidIgnore=$(echo "$pidIgnore" | tr ' ' ',')
    cpus=""
    time curl http://127.0.0.1:8080/function/$1 -d '{"n":"'$2'"}' \
        & sleep 0.05

    pid=$(pidof python3 -o $pidIgnore)
    while :;
    do
        check_pid=$(pidof python3 -o $pidIgnore)
        if [ -z "$check_pid" ]; then
            break
        else 
            cpus=$(echo $(taskset -cp $pid) | awk -F 'list: ' '{print $2}')
            echo $cpus
            sleep 1
        fi
    done
}

get_numa_usage() 
{
    local func=$1
    local n=$2
    local env=$3
    local lang=python3

    echo | sudo tee ./$func/$env\_$n\_$lang.csv
    pidIgnore=$(pidof curl)
    pidIgnore=$(echo "$pidIgnore" | tr ' ' ',')
    
    sudo pcm-memory 0.1 -csv=./$func/$env\_$n\_$lang.csv -f -silent &
    # let pcm spin up
    sleep 2
    date
    # curl http://127.0.0.1:8080/function/$func -d '{"n":"'$n'"}' 
    # curl -i http://127.0.0.1:8080/function/matmul-cxl-go -d '{"n":"1000"}'
    # sudo numactl --cpunodebind 0 --membind 1 -- python3 /home/cc/functions/run_bench/normal_run/matmul.py $n
    time curl http://127.0.0.1:8080/function/matmul-cxl -d '{"n":"'$n'"}' & \
        sleep 0.5
    # pcmPid=$(echo $!)
    # echo $pcmPid
    # sleep 0.05
    while :;
    do
        check_pid=$(pidof curl)
        echo $check_pid
        if [ -z "$check_pid" ]; then
            # sudo kill -9 $pcmPid
            echo "killing pcm!!"
            date
            sleep 0.5
            sudo pkill -9 pcm-memory
            break
        else
            sleep 1
        fi
    done
}

run_one_func_bench()
{
    local func=matmul
    local env=cxl
    for n in 13000
    do
        # drop page cache 
        sync; echo 1 | sudo tee /proc/sys/vm/drop_caches
        # evict dynamic libs
        # while IFS= read -r line; do vmtouch -e $line >> evict_res.log 2>&1; done < "./normal_run/to_evict.txt"
        sleep 2
        echo "testing" $func with size $n
        get_numa_usage $func $n $env
    done
}

# $1: function to run <matmul>
# $2: env <base, cxl>
run_one_func_bench

