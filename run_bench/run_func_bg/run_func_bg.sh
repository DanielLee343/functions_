resnet_training()
{
    echo > resnet_training_res.log
    for bs in 16 32 64 128 256 512
    do
        for env in base cxl
        do
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

# resnet_training_bm