resnet_training()
{
    echo > resnet_training_res.log
    for bs in 16 32 64 128 256 512
    do
        for env in base cxl interleave
        do
            echo "doing $env for $bs" >> resnet_training_res.log
            curl http://127.0.0.1:8080/function/resnet-training-$env -d '{"bs":"'$bs'"}' >> resnet_training_res.log
            echo finished $env with bs $bs
            sleep 2
        done
    done
}

img_proc()
{
    echo > img_proc_res.log
    for img_size in 5 10 30 63 127 191 287
    do
        for env in base cxl
        do
            echo "doing $env for $img_size" >> img_proc_res.log
            curl http://127.0.0.1:8080/function/img-$env -d '{"img_size":"'$img_size'mb"}' >> img_proc_res.log
            echo finished $env with img_size $img_size
            sleep 2
        done
    done
}

matmul_go()
{
    echo > matmul_go.log
    for n in 5000 7500 10000 12500 15000 
    do
        for env in cxl
        do
            echo "doing $env for $n" >> matmul_go.log
            curl http://127.0.0.1:8080/function/matmul-$env-go -d '{"n":"'$n'"}' >> matmul_go.log
            echo finished $env with n $n
            sleep 2
        done
    done
}

cifar100()
{
    echo > serve_res.log
    for net in squeezenet resnet50 resnet152 inceptionv4
    do
        for portion in 1 5 10
        do
            for env in base cxl
            do
                echo "doing portion $portion for env $env" >> serve_res.log
                curl -i http://127.0.0.1:8080/function/cifar100-$env -d '{"net":"'$net'","task":"serve","portion":"'$portion'"}' >> serve_res.log
                # echo finished $env with batches $batches
                sleep 2
                sudo sync && echo 1 | sudo tee /proc/sys/vm/drop_caches
            done
        done
    done
}

graph()
{
    echo > graph_res.log
    for algo in pagerank mst bfs
    do
        for size in 100000 500000 1000000 2000000
        do
            for env in base cxl
            do
                echo "doing $algo $size $env " >> graph_res.log
                curl http://127.0.0.1:8080/function/graph-$env -d '{"algo":"'$algo'","size":"'$size'"}' >> graph_res.log
                sleep 2
            done
        done
    done
}

cifar100