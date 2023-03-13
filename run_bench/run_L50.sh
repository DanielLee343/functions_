total_mem_needed=1340
et=50
MEMEATER=/home/cc/Pond/memeater

sudo killall memeater >/dev/null 2>&1
sleep 10

NODE0_FREE_MEM=$(sudo numactl --hardware | grep 'node 0 free' | awk '{print $4}')
((NODE0_FREE_MEM -= 520))
# echo $NODE0_FREE_MEM
APP_MEM_ON_NODE0=$(echo "$total_mem_needed*$et/100.0" | bc)
echo $APP_MEM_ON_NODE0
MEM_SHOULD_RESERVE=$((NODE0_FREE_MEM - APP_MEM_ON_NODE0))
MEM_SHOULD_RESERVE=${MEM_SHOULD_RESERVE%.*}
echo $MEM_SHOULD_RESERVE

if [[ $MEM_SHOULD_RESERVE -gt 0 ]]; then
    # Make sure that MemEater is reserving memory from Node 0
    echo "spinning memeater"
    numactl --cpunodebind 0 --membind 0 -- $MEMEATER ${MEM_SHOULD_RESERVE} &
    # mapid=$!
    # Wait until memory eater consume all destined memory
    sleep 120
fi

curl -i http://127.0.0.1:8080/function/resnet-training-l50 -d '{"bs":"64"}' 

sudo killall memeater >/dev/null 2>&1
sleep 10