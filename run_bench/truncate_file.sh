#!/bin/bash

filename="/home/cc/functions/run_bench/playground/gif/chunk_2.txt"
head -n -6000 $filename > file_new.txt
mv file_new.txt $filename
