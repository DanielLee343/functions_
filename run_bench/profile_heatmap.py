import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import sys

PAGE_SIZE = 4096


def to_csv(df):
    df.to_csv('/home/cc/functions/run_bench/playground/gif/test.csv', index=False)


def plot_heatness_dist(df):
    # column_to_plot = df['Column1']
    plt.rcdefaults()
    plt.hist(df, bins=10)  # Adjust the number of bins as desired

    # Add labels and title to the plot
    plt.xlabel('Range')
    plt.ylabel('Memory Access Frequency')
    plt.title('Distribution of Heatness')
    global workload_name
    output_dist = "/home/cc/functions/run_bench/playground/{}/temperatur_distribution.png".format(
        workload_name)
    plt.savefig(output_dist)

# def slope():
    # slopes = (df['y'] - df['y'].shift(1)) / (df['x'] - df['x'].shift(1))

    # # Find the index of the largest slope
    # largest_slope_index = slopes.abs().idxmax()

    # # Get the largest slope and the corresponding x and y values
    # largest_slope = slopes.loc[largest_slope_index]
    # x_value = df['x'].loc[largest_slope_index]
    # y_value = df['y'].loc[largest_slope_index]

    # # Print the largest slope and the corresponding x and y values
    # print("Largest Slope:", largest_slope)
    # print("Corresponding x:", x_value)
    # print("Corresponding y:", y_value)

# Given the none-zero, sorted heatness dataframe, and threshold of cdf to split, return the subset of df, where the heatness is larger than the value


def get_cdf_thresh_chunk(filtered_sorted_df, thresh=0.8):
    cdf_split_index = int(thresh * len(filtered_sorted_df))
    # print(cdf_split_index)
    cdf_split_raw_temp = filtered_sorted_df.iloc[cdf_split_index]['temp']
    print("cdf thresh heat is: ", cdf_split_raw_temp)
    mask = filtered_sorted_df['temp'] > cdf_split_raw_temp
    cdf_thresh_chunk = filtered_sorted_df[mask]
    return cdf_thresh_chunk

# Given the heatness of the none-zero, sorted df, plot the cdf of heatness


def plot_heatness_cdf(filtered_sorted_temp, filename):
    plt.rcdefaults()
    global workload_name
    cdf_y = np.arange(1, len(filtered_sorted_temp) + 1) / \
        len(filtered_sorted_temp)
    plt.plot(filtered_sorted_temp, cdf_y, linestyle='-', color='red')
    plt.xlabel('Memory Access Frequency')
    plt.ylabel('CDF')
    plt.title('CDF of heatness of {}'.format(workload_name))
    plt.grid(False)
    output_cdf = "/home/cc/functions/run_bench/playground/{}/{}.png".format(
        workload_name, filename)
    plt.savefig(output_cdf)


def get_heatness_thresh_chunk(filtered_sorted_df, temp_split_percent=0.8):
    largest_temp = filtered_sorted_df['temp'].iloc[-1]
    # print("largest temp:", largest_temp)
    temp_split_value = (temp_split_percent * largest_temp)
    print("temp_split_value: ", temp_split_value)
    # differences = np.abs(filtered_sorted_df['temp'] - temp_split_value)
    # closest_index = differences.idxmin()
    # heatness_split_raw_temp = filtered_sorted_df.loc[closest_index]['temp']
    mask = filtered_sorted_df['temp'] > temp_split_value
    heatness_thresh_chunk = filtered_sorted_df[mask]
    return heatness_thresh_chunk

# this will return a tuple contains (mmap start address, hot region start, hot region end)


def check_intersection(range1, range2):
    mmap_start, mmap_end = range1
    heat_start, heat_end = range2

    if mmap_end < heat_start or heat_end < mmap_start:
        return None
    else:
        intersect_start = max(mmap_start, heat_start)
        intersect_end = min(mmap_end, heat_end)
        intersect_range = (mmap_start, intersect_start, intersect_end)
        if mmap_start > intersect_start:
            print("mmaped region above hot region starts, need to pay attention")
        assert intersect_end > intersect_start, "wrong"
        return intersect_range


def check_combine(range1, range2):
    A, B = range1
    C, D = range2

    if B < C or D < A:
        return None
    else:
        lower_bound = min(A, C)
        max_bound = max(B, D)
        assert max_bound > lower_bound, "wrong"
        return (lower_bound, max_bound)

# merge adjacent ranges until no ranges overlap


def merge_adj(heat_set):
    # new_set = set()
    # tmp_set = heat_set
    # for item1_to_merge in heat_set:
    #     remaining_counter = len(heat_set) - 1
    #     for item2_to_merge in heat_set:
    #         if item1_to_merge != item2_to_merge:
    #             latent_range = check_combine(item1_to_merge, item2_to_merge)
    #             if latent_range is None:
    #                 remaining_counter -= 1
    #             if latent_range is not None:
    #                 # heat_set.remove(item1_to_merge)
    #                 # heat_set.remove(item2_to_merge)
    #                 print("latent range:", latent_range, "is the merged of ", item1_to_merge, " and ", item2_to_merge)
    #                 new_set.add(latent_range)
    #     if remaining_counter == 0:
    #         new_set.add(item1_to_merge)

    # before merge, sort the heat set using the heatness, and delete low heatness ones
    heat_set = sorted(heat_set, key=lambda x: x[-1])
    print("before truncate: ", len(heat_set))
    num_drop_off = int(len(heat_set) * 0.4)
    del heat_set[:num_drop_off]
    print("after truncate: ", len(heat_set))
    third_elements = [t[2] for t in heat_set]
    plot_heatness_cdf(third_elements, "to_drop_off")
    # heat_set = [tuple(item[:2]) if len(item) >
    #             2 else item for item in heat_set] # -> this will give you list that contains dups, will cause error when merging!
    heat_set = {(x, y) for x, y, _ in heat_set}

    while True:
        merged = set()
        for tuple1 in heat_set:
            remaining_counter = len(heat_set) - 1
            for tuple2 in heat_set:
                if tuple1 != tuple2:
                    if tuple1[1] >= tuple2[0] and tuple1[0] <= tuple2[1]:
                        merged.add(
                            (min(tuple1[0], tuple2[0]), max(tuple1[1], tuple2[1])))
                    else:
                        remaining_counter -= 1
            if remaining_counter == 0:
                merged.add(tuple1)
        if merged == heat_set:
            break
        else:
            heat_set = merged.copy()
    return heat_set


def merge_heats(filtered_sorted_all, abs_all):
    heat_list = []  # a list contains merged tuples (start_addr, end_addr)
    heat_set = set()  # a set contains merged tuples (start_addr, end_addr)
    considered_heats = set()  # a list contains index that has been considered
    smallest_temp = filtered_sorted_all.iloc[0]
    merge_expand_thresh = 0.5
    merge_expand_value = smallest_temp['temp'] * merge_expand_thresh
    # print("smallest:", smallest_temp)
    print("smallest:", merge_expand_value)
    # time.sleep(10)
    for index, latent_heat_row in filtered_sorted_all.iterrows():
        heats_sum = 0
        # if current addr is considered, skip
        if index in considered_heats:
            continue
        # else, not considered, then mark current addr with curr time as considered
        considered_heats.add(index)
        cur_row_time = latent_heat_row['abs_time']
        start_index = 0
        end_index = 0
        prev_index = index
        next_index = index
        while abs_all.loc[prev_index]['temp'] >= merge_expand_value and abs_all.loc[prev_index]['abs_time'] == cur_row_time:
            considered_heats.add(prev_index)
            heats_sum += abs_all.loc[prev_index]['temp']
            prev_index -= 1
        # once get out, prev_index either < 0.1, or get into previous time range
        # if latter, set the start_index to its next
        if abs_all.loc[prev_index]['abs_time'] != cur_row_time:
            print("time underflow, updating to next time range")
            start_index = prev_index + 1
        else:  # set start_index to the first row in current time range that is not considered as hot
            start_index = prev_index

        # do the same for end_index
        while abs_all.loc[next_index]['temp'] >= merge_expand_value and abs_all.loc[next_index]['abs_time'] == cur_row_time:
            considered_heats.add(next_index)
            heats_sum += abs_all.loc[next_index]['temp']
            next_index += 1
        if abs_all.loc[next_index]['abs_time'] != cur_row_time:
            print("time overflow, updating to previous time range")
            end_index = next_index - 1
        else:
            end_index = next_index

        assert abs_all.loc[start_index]['abs_time'] == abs_all.loc[end_index][
            'abs_time'], "Timestamp of start_index and end_index must be matched!"
        if end_index == start_index:
            # standalone heatness, append prev and next
            assert end_index == index, "Logic bug!"
            # abs_all.loc[end_index]['abs_time'], -> for later
            cur_hot_range = (int(abs_all.loc[end_index - 1]['abs_addr']), int(
                abs_all.loc[end_index + 1]['abs_addr']), heats_sum)
        else:
            assert start_index < end_index, "Start index must be smaller than end index!"

            cur_hot_range = (int(abs_all.loc[start_index]['abs_addr']), int(
                abs_all.loc[end_index]['abs_addr']), heats_sum)
        # cur_hot_range = tuple(int(item) for item in cur_hot_range)
        # if cur_hot_range not in heat_list:
        #     heat_list.append(cur_hot_range)
        heat_set.add(cur_hot_range)
        # print(cur_hot_range)
        # break
    # merge adjacent ranges
    merged_heat_set = merge_adj(heat_set)

    return heat_set, merged_heat_set


def parse_mmap_df():
    global workload_name
    call_stack_df = pd.read_csv('/home/cc/functions/run_bench/playground/{}/intercepted.log'.format(
        workload_name), sep=',', names=['timestamp', 'syscall', 'addr_dec', 'addr_hex', 'size'], on_bad_lines="skip")
    call_stack_df.dropna(inplace=True)
    call_stack_df.reset_index(drop=True, inplace=True)
    mmap_df = call_stack_df[call_stack_df['syscall'] == 'mmap']
    # mmap_df['size'] = mmap_df['size'].astype(int)
    # print(mmap_df)
    mmap_ranges = []  # a list contains mmap start and end addr
    for index, mmap_row in mmap_df.iterrows():
        mmap_range = (int(mmap_row['addr_dec']), int(
            mmap_row['addr_dec']) + int(mmap_row['size']))
        mmap_ranges.append(mmap_range)
    # print(mmap_ranges)
    return mmap_ranges


def get_intersect(mmap_ranges, merged_set):
    to_DRAM_regions = []
    for mmap_range in mmap_ranges:
        for heat_item in merged_set:
            curr_region = check_intersection(mmap_range, heat_item)
            if curr_region is not None:
                to_DRAM_regions.append(curr_region)
    return to_DRAM_regions


def write_res(hot_regions, file_path):
    with open(file_path, 'w') as file:
        for tuple_data in hot_regions:
            line = ','.join(str(element) for element in tuple_data)
            file.write(line + '\n')

# def get_addr_index(merged_set, abs_all):
#     abs_all.set_index('abs_addr', inplace=True)
#     for each_region in merged_set:
#         start_index = abs_all.index.get_loc(each_region[0])
#         end_index = abs_all.index.get_loc(each_region[1])
#         print(start_index, end_index)


def align_2_page(heat_set):
    heat_list = [list(t) for t in heat_set]
    for each_range in heat_list:
        start = each_range[0]
        end = each_range[1]
        remainder_start = start % PAGE_SIZE
        remainder_end = end % PAGE_SIZE
        if remainder_start <= 2048:
            start -= remainder_start
            # print("start:", start)
        else:
            start += PAGE_SIZE - remainder_start
            # print("start:", start)
        if remainder_end <= 2048:
            end -= remainder_end
            # print("end:", end)
        else:
            end += PAGE_SIZE - remainder_end
            # print("end:", end)
        each_range[0] = start
        each_range[1] = end
    print("modified:", heat_list)
    return heat_list


if __name__ == "__main__":
    workload_name = sys.argv[1]
    thresh = float(sys.argv[2])
    if thresh is None:
        thresh = 0.1
    abs_all = pd.read_csv('/home/cc/functions/run_bench/playground/{}/abs_addr_time.txt'.format(
        workload_name), sep='\t', names=['abs_time', 'abs_addr', 'temp'])
    sorted_abs_all = abs_all.sort_values(by='temp')
    # print(sorted_abs_all)
    filtered_sorted_all = sorted_abs_all[sorted_abs_all['temp'] != 0.0]

    plot_heatness_cdf(filtered_sorted_all['temp'], "heat_cdf")
    # plot_heatness_dist(filtered_sorted_all['temp'])
    # chunks = get_cdf_thresh_chunk(filtered_sorted_all, 0.5)
    # default: 1 - 0.1 = 90% of the hotest area will be put to DRAM
    chunks = get_heatness_thresh_chunk(filtered_sorted_all, thresh)
    # chunks = get_cdf_thresh_chunk(filtered_sorted_all, thresh)
    print(chunks)
    if len(chunks) == 0:
        print("no hot regions observed")
        exit(0)

    # # heat_list: [(time_start, time_end, addr_start, addr_end, heat_weight)]
    heat_set, merged_set = merge_heats(chunks, abs_all)
    print("len org heat_set: ", len(heat_set))
    print("len merged_set: ", len(merged_set))
    print("not aligned:", merged_set)
    as_heats = align_2_page(merged_set)

    # profile mmap call stack
    # TODO: modify porter_lib, comma, strict row elem representation
    # mmap_ranges = parse_mmap_df()
    # print("mmap intercepted length: ", len(mmap_ranges))
    # to_DRAM_regions = get_intersect(mmap_ranges, merged_set)
    # print("final intersection length: ", len(to_DRAM_regions))
    # print(to_DRAM_regions)
    write_res(as_heats, "/home/cc/res.txt")
