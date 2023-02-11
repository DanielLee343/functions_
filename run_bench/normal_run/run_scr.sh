# python3 ./matmul.py 20000

monitor_resource_util()
{
    while true; do
        local o=$(sudo numactl --hardware)
        local node0_free_mb=$(echo "$o" | grep "node 0 free" | awk '{print $4}')
		local node1_free_mb=$(echo "$o" | grep "node 1 free" | awk '{print $4}')
        echo "$(date +"%D %H%M%S") ${node0_free_mb} ${node1_free_mb}"
        #pidstat -r -u -d -l -p ALL -U -h 5 100000000 > pidstat.log &
        sleep 5
    done
}