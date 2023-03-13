curl -i http://127.0.0.1:8080/function/resnet-training-cxl -d '{"bs":"512"}' & sleep 1
check_pid=$(ps aux | grep 'python3 index.py' | grep -v grep | awk '{print $2}')

while [ -d "/proc/${check_pid}" ]
do
    rss_in_kb=$(ps aux | grep 'python3 index.py' | grep -v grep | awk '{print $6}')
    rss_in_mb=$(echo "$rss_in_kb/1024" | bc)
    rss_in_mb=${rss_in_mb%.*}
    echo $rss_in_mb
    sleep 1
done
# rss_in_kb=$(ps aux | grep './faas-netes' | grep -v grep | awk '{print $6}')
