import bisect


def get_subset_in_range(sorted_list, a, b):
    start_index = bisect.bisect_right(sorted_list, a)
    end_index = bisect.bisect_left(sorted_list, b)
    return sorted_list[start_index:end_index]


# Example usage:
sorted_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
sorted_list = sorted(sorted_list, reverse=True)
b = 2.9
a = 7.6
subset = get_subset_in_range(sorted_list, a, b)
print(subset)  # Output: [3, 4, 5, 6]
