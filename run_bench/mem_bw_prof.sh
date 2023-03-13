# !/bin/bash

#Basic information
#perf stat -e cache-misses,cache-references -p 32543
#perf stat -e LLC-misses -C 2 -a -p 1234

#$1 PID of the target to measure
#$2 Desired measurement interval in seconds

MEASUREMENT_PID=$1
MEASUREMENT_TIME=$2

echo "Measuring on PID:" $MEASUREMENT_PID

lscpu --all --parse | awk -F: '/^[^#]/ { split($0, cpusinfo, ","); print cpusinfo[1] " " cpusinfo[4]}' > lscpu.txt 
NUM_CPU=(`cat lscpu.txt | wc `)

declare -A CPU_NODE_MAP
declare -A NODE_CPU_MAP
declare -A NUMA_NODE_CORES
for ((i=0;i<$NUM_CPU;i++)); do
	CPU_NODE=(`sed -n "$((i+1))"p lscpu.txt | awk '{print $2}'`)
    echo $CPU_NODE
	CPU_NODE_MAP[$i]=$CPU_NODE
	NODE_CPU_MAP[$CPU_NODE]=$i
done
for ((i=0;i<${#NODE_CPU_MAP[@]};i++)); do
	NUMA_NODE_CORES_TEMP=""
	for ((ii=0;ii<$NUM_CPU;ii++)); do
		if [[ ${CPU_NODE_MAP[$ii]} == $i ]]; then
			NUMA_NODE_CORES_TEMP+="$ii,"
		fi
	done
	NUMA_NODE_CORES[$i]=${NUMA_NODE_CORES_TEMP:0:-1}
done

sudo sleep 1

#BW

declare -A PERF_PPIDS
declare -A CORES_LLC_MISSES
PAGESIZE=(`getconf PAGESIZE`)

echo Profiling starts
for ((i=0;i<${#NUMA_NODE_CORES[@]};i++)); do
	sudo perf stat -e LLC-misses -C ${NUMA_NODE_CORES[$i]} -I 1000 -p $MEASUREMENT_PID 2> perf_numa_${i}_LLC_misses.txt &
	PERF_PPIDS[$i]=$!
	echo Numa $i perf Parent PID: ${PERF_PPIDS[$i]}
done

echo "Waiting on profiling to finish"
sleep $MEASUREMENT_TIME
for ((i=0;i<${#NUMA_NODE_CORES[@]};i++)); do
	PERF_PID=(`pgrep -P ${PERF_PPIDS[$i]}`)
	echo killing $PERF_PID
	sudo kill -INT $PERF_PID
done

echo Profiling finishes
for ((i=0;i<${#NUMA_NODE_CORES[@]};i++)); do
	NUM_DATA_POINTS=(`cat perf_numa_${i}_LLC_misses.txt | awk -F: '/^[^#]/ { print $0}' | wc`)
	DATA_POINT_LAST_TIME_ELAPSED=0
	echo "NUMA NODE $i BW:"
	echo -e "TIMESTEP\tBW(Bytes/sec)"
	for ((ii=0;ii<$NUM_DATA_POINTS;ii++)); do
		DATA_POINT_TIME_ELAPSED=(`cat perf_numa_${i}_LLC_misses.txt | awk -F: '/^[^#]/ { print $0}' | sed -n "$((ii+1))"p | awk '{print $1}'`)
		DATA_POINT_LLC_MISSED=(`cat perf_numa_${i}_LLC_misses.txt | awk -F: '/^[^#]/ { print $0}' | sed -n "$((ii+1))"p | awk '{print $2}'`)
		DATA_POINT_BW=0
		if [[ $DATA_POINT_LLC_MISSED != "<not" ]]; then
			DATA_POINT_LLC_MISSED=(`echo $DATA_POINT_LLC_MISSED | sed 's/,//g'`)
			DATA_POINT_BW=(`bc <<< " $DATA_POINT_LLC_MISSED * $PAGESIZE / ( $DATA_POINT_TIME_ELAPSED - $DATA_POINT_LAST_TIME_ELAPSED ) " `)
		fi

		echo -e "$ii\t\t$DATA_POINT_BW"

		DATA_POINT_LAST_TIME_ELAPSED=$DATA_POINT_TIME_ELAPSED
	done
done

#RSS
#/usr/bin/smem -p 32543 -c "pss uss"
#ps 32543
