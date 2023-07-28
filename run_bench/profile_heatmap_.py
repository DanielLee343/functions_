import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import sys
PAGE_SIZE = 4096


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
        # break
        if merged == heat_set:
            break
        else:
            heat_set = merged.copy()
    return heat_set


def merge_ranges_fast(ranges):
    # Sort the ranges based on the start value
    sorted_ranges = sorted(ranges, key=lambda x: x[0])
    # print(len(sorted_ranges))

    merged_ranges = set()
    current_range = sorted_ranges[0]

    for next_range in sorted_ranges[1:]:
        if next_range[0] <= current_range[1]:
            # Overlapping or adjacent ranges, update the end value
            current_range = (current_range[0], max(
                current_range[1], next_range[1]))
        else:
            # Non-overlapping range, add the current range to the merged list
            if (current_range[0] != current_range[1]):
                merged_ranges.add(current_range)
            current_range = next_range

    # Add the last remaining range to the merged list
    if (current_range[0] != current_range[1]):
        merged_ranges.add(current_range)

    return merged_ranges


def expand_adj(heat_sum_sort_by_heat_hotest, heat_sum_sort_by_addr, addresses_asc):
    considered_heats = set()
    heat_set = set()

    for each_hot_region in heat_sum_sort_by_heat_hotest:
        each_hot_region_addr = each_hot_region[0]
        if each_hot_region_addr in considered_heats:
            continue
        considered_heats.add(each_hot_region_addr)
        # cur_hot_addr_index = heat_sum_dict[each_hot_region_addr]
        cur_hot_addr_index = addresses_asc.index(each_hot_region_addr)
        # print(cur_hot_addr_index)
        start_index = 0
        end_index = 0
        prev_index = cur_hot_addr_index
        next_index = cur_hot_addr_index
        prev_addr_diff = 0
        prev_addr_diff = heat_sum_sort_by_addr[cur_hot_addr_index -
                                               1][0] - heat_sum_sort_by_addr[cur_hot_addr_index][0]
        prev_addr_diff_2 = heat_sum_sort_by_addr[cur_hot_addr_index -
                                                 2][0] - heat_sum_sort_by_addr[cur_hot_addr_index - 1][0]

        # largest sampled address
        if cur_hot_addr_index + 1 == len(heat_sum_sort_by_addr) \
                and heat_sum_sort_by_addr[prev_index][1] >= merge_low_value and heat_sum_sort_by_addr[prev_index][1] <= merge_high_value:
            end_index = cur_hot_addr_index
            correct_addr_diff = prev_addr_diff
            while heat_sum_sort_by_addr[prev_index][1] >= merge_low_value and heat_sum_sort_by_addr[prev_index][1] <= merge_high_value:
                considered_heats.add(prev_index)
                if heat_sum_sort_by_addr[prev_index - 1][0] - heat_sum_sort_by_addr[prev_index][0] != correct_addr_diff:
                    break
                prev_index -= 1
            start_index = prev_index
            cur_hot_range = (int(addresses_asc[start_index]), int(
                addresses_asc[end_index]))
            heat_set.add(cur_hot_range)
            continue
        elif cur_hot_addr_index + 2 == len(heat_sum_sort_by_addr) \
                and heat_sum_sort_by_addr[prev_index][1] >= merge_low_value and heat_sum_sort_by_addr[prev_index][1] <= merge_high_value:
            end_index = cur_hot_addr_index + 1
            correct_addr_diff = prev_addr_diff
            while heat_sum_sort_by_addr[prev_index][1] >= merge_low_value and heat_sum_sort_by_addr[prev_index][1] <= merge_high_value:
                considered_heats.add(prev_index)
                if heat_sum_sort_by_addr[prev_index - 1][0] - heat_sum_sort_by_addr[prev_index][0] != correct_addr_diff:
                    break
                prev_index -= 1
            start_index = prev_index
            cur_hot_range = (int(addresses_asc[start_index]), int(
                addresses_asc[end_index]))
            heat_set.add(cur_hot_range)
            continue
        next_addr_diff = heat_sum_sort_by_addr[cur_hot_addr_index +
                                               1][0] - heat_sum_sort_by_addr[cur_hot_addr_index][0]
        next_addr_diff_2 = heat_sum_sort_by_addr[cur_hot_addr_index +
                                                 2][0] - heat_sum_sort_by_addr[cur_hot_addr_index + 1][0]
        if next_addr_diff == next_addr_diff_2 and prev_addr_diff != prev_addr_diff_2:
            # reaching the boundary of start of region, need to checking forward
            start_index = cur_hot_addr_index
            correct_addr_diff = next_addr_diff
            while heat_sum_sort_by_addr[next_index][1] >= merge_low_value and heat_sum_sort_by_addr[next_index][1] <= merge_high_value:
                considered_heats.add(next_index)
                if next_index + 1 == len(heat_sum_sort_by_addr):
                    break
                if heat_sum_sort_by_addr[next_index + 1][0] - heat_sum_sort_by_addr[next_index][0] != correct_addr_diff:
                    break
                next_index += 1
            end_index = next_index
            # print("1st situ:", heat_sum_sort_by_addr[end_index][1])
        elif next_addr_diff != next_addr_diff_2 and prev_addr_diff == prev_addr_diff_2:
            # reaching ... end of region, need to check backward
            end_index = cur_hot_addr_index
            correct_addr_diff = prev_addr_diff
            while heat_sum_sort_by_addr[prev_index][1] >= merge_low_value and heat_sum_sort_by_addr[prev_index][1] <= merge_high_value:
                considered_heats.add(prev_index)
                if heat_sum_sort_by_addr[prev_index - 1][0] - heat_sum_sort_by_addr[prev_index][0] != correct_addr_diff:
                    break
                prev_index -= 1
            start_index = prev_index
            # print("2nd situ:", heat_sum_sort_by_addr[start_index][1])
        else:
            while heat_sum_sort_by_addr[next_index][1] >= merge_low_value and heat_sum_sort_by_addr[next_index][1] <= merge_high_value:
                considered_heats.add(next_index)
                if next_index + 1 == len(heat_sum_sort_by_addr):
                    break
                if heat_sum_sort_by_addr[next_index + 1][0] - heat_sum_sort_by_addr[next_index][0] != next_addr_diff:
                    break
                next_index += 1
            end_index = next_index
            while heat_sum_sort_by_addr[prev_index][1] >= merge_low_value and heat_sum_sort_by_addr[prev_index][1] <= merge_high_value:
                considered_heats.add(prev_index)
                if heat_sum_sort_by_addr[prev_index - 1][0] - heat_sum_sort_by_addr[prev_index][0] != prev_addr_diff:
                    break
                prev_index -= 1
            start_index = prev_index
            # print("3rd start:", heat_sum_sort_by_addr[start_index][1])
            # print("3rd end:", heat_sum_sort_by_addr[end_index][1])

        if end_index == start_index:  # standalone heat value, append prev and next
            assert end_index == cur_hot_addr_index, "Logic bug!"
            cur_hot_range = (int(
                addresses_asc[cur_hot_addr_index - 1]), int(addresses_asc[cur_hot_addr_index + 1]))
        else:
            assert start_index < end_index, "Start index must be smaller than end index!"
            cur_hot_range = (int(addresses_asc[start_index]), int(
                addresses_asc[end_index]))
        heat_set.add(cur_hot_range)
        # break
    print(len(heat_set))
    print("before merge")
    print_hot_ranges(heat_set, addresses_asc)
    return heat_set


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
        if start == end:
            heat_list.remove(each_range)
        else:
            each_range[0] = start
            each_range[1] = end
    print("aligned:", heat_list)
    return heat_list


def print_hot_ranges(merged_set, addresses_asc):
    for each in merged_set:
        start_index = addresses_asc.index(each[0])
        end_index = addresses_asc.index(each[1])
        print("heatstart:", heat_sum_sort_by_addr[start_index],
              "heat_end:", heat_sum_sort_by_addr[end_index])


def get_hot_regions(sampled_heats):
    sampled_page_ranges = set()
    for each_sample in sampled_heats:
        addr = each_sample[0]
        page_index = int(addr / PAGE_SIZE)
        sampled_page_ranges.add((page_index, page_index + 1))
    return sampled_page_ranges


if __name__ == "__main__":
    workload_name = sys.argv[1]
    thresh = float(sys.argv[2])
    if sys.argv[3] == None:
        hot_rand_cold = "hot"
    else:
        hot_rand_cold = sys.argv[3]
    abs_all = pd.read_csv('/home/cc/functions/run_bench/playground/{}/abs_addr_time.txt'.format(
        workload_name), sep='\t', names=['abs_time', 'abs_addr', 'temp'])
    abs_all_not_zero = abs_all[abs_all['temp'] != 0.0]
    sorted_none_zero = abs_all_not_zero.sort_values(by='temp')
    plot_heatness_cdf(sorted_none_zero['temp'], "heat_cdf")
    grouped_df = abs_all_not_zero.groupby(abs_all_not_zero.iloc[:, 1])
    heat_sum = []
    for addr, group_data in grouped_df:
        cur_addr_heat_sum = group_data.iloc[:, 2].sum()
        heat_sum.append((addr, cur_addr_heat_sum))
        # break
    # sort by hotness, descending
    heat_sum_sort_by_heat = sorted(heat_sum, key=lambda x: x[1], reverse=True)
    heat_sum_sort_by_addr = sorted(
        heat_sum, key=lambda x: x[0], reverse=False)  # sort by addr, ascending
    merge_expand_thresh = 0.5
    merge_low_value = 0
    merge_high_value = sys.maxsize
    if hot_rand_cold == "hot":
        sampled_heats = heat_sum_sort_by_heat[0:int(
            len(heat_sum_sort_by_heat)*(1 - thresh))]

        merge_low_value = sampled_heats[-1][1] * merge_expand_thresh
        merge_high_value = sampled_heats[0][1]
    elif hot_rand_cold == "rand":
        # import random
        # num_sample = int(len(heat_sum_sort_by_heat) * (1 - thresh))
        # merge_high_value = sys.maxsize
        # while merge_high_value > 6000 or merge_high_value < 2000:
        #     sampled_heats = random.sample(heat_sum_sort_by_heat, num_sample)
        import bisect
        heat_sum_sort_by_heat = sorted(
            heat_sum_sort_by_heat, key=lambda x: x[1], reverse=False)
        merge_high_value = 7000
        merge_low_value = 1000
        start_index = bisect.bisect_left(
            [t[1] for t in heat_sum_sort_by_heat], merge_low_value)
        end_index = bisect.bisect_right(
            [t[1] for t in heat_sum_sort_by_heat], merge_high_value)
        sampled_heats = heat_sum_sort_by_heat[start_index:end_index]
        sampled_heats = sorted(
            sampled_heats,  key=lambda x: x[1], reverse=True)
        print("sampled_heats len:", len(sampled_heats))
        # sampled_heats = sorted(
        #     sampled_heats, key=lambda x: x[1], reverse=True)
        #     merge_low_value = sampled_heats[-1][1] * merge_expand_thresh
        #     merge_high_value = sampled_heats[0][1]
        #     print("cur merge_high_value {}, try again...".format(merge_high_value))

    elif hot_rand_cold == "cold":
        sampled_heats = heat_sum_sort_by_heat[-int(
            len(heat_sum_sort_by_heat)*(1 - thresh)):]
        # merge_low_value = sampled_heats[int(len(sampled_heats) / 2)][1]
        merge_low_value = sampled_heats[-1][1] * merge_expand_thresh
        merge_high_value = sampled_heats[0][1]
    else:
        print("wrong setting!!")
        exit(1)

    print("low allowed bar:", merge_low_value)
    print("high allowed bar:", merge_high_value)

    addresses_asc = [item[0] for item in heat_sum_sort_by_addr]
    heat_set = expand_adj(sampled_heats,
                          heat_sum_sort_by_addr, addresses_asc)
    # merged_set_slow = merge_adj(heat_set)
    merged_set = merge_ranges_fast(heat_set)
    print("after merge")
    print_hot_ranges(merged_set, addresses_asc)
    print()
    aligned_heats = align_2_page(merged_set)
    write_res(aligned_heats, "/home/cc/res.txt")

    # page_indices = get_hot_regions(sampled_heats)
    # print("num ranges: ", len(page_indices))
    # merged_set = merge_ranges_fast(page_indices)
    # merged_set = [(page_start * PAGE_SIZE, page_end * PAGE_SIZE)
    #               for page_start, page_end in merged_set]

    # print("final merged len: ", len(merged_set))
    # # assert merged_set == merged_set_slow, "merge aresults re different"
    # write_res(merged_set, "/home/cc/res.txt")
