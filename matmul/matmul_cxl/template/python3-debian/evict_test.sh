while IFS= read -r line; do vmtouch -e $line >> evict_res.log 2>&1; done < "/home/app/files_to_evict.txt"