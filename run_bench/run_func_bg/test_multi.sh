for i in {1..5}
do
    curl -i http://127.0.0.1:8080/function/matmul-cxl-go -d '{"n":"5000"}' &
done