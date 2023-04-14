set datafile separator ','
set terminal png
set output output_file
set title wl_title
set xlabel "Time (s)"
set ylabel "Bandwidth (MB/s)"
plot input_file \
    using 1:2 title 'sock0' with lines ls 1, \
    '' using 1:3 title 'sock1' with lines ls 2