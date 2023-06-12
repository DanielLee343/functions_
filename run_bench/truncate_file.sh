#!/bin/bash

filename="/home/cc/functions/run_bench/playground/gif/abs_addr_time.txt"
head -n -6000 $filename > file_new.txt
mv file_new.txt $filename
