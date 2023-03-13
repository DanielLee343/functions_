for i in {1..2000}
do
    curl http://127.0.0.1:8080/function/matmul-cxl-go -d '{"n":"100"}' &
    sleep 0.01
done