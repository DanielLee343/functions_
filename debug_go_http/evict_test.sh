input="./files_to_evict.txt"
echo > evict_res.log
while IFS= read -r line
do
    # echo $line
    vmtouch -e $line >> evict_res.log 2>&1
done < $input