import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def to_csv(df):
    df.to_csv('/home/cc/functions/run_bench/playground/gif/test.csv', index=False)

def plot_heatness_dist(df):
    # column_to_plot = df['Column1']

    plt.hist(df, bins=10)  # Adjust the number of bins as desired

    # Add labels and title to the plot
    plt.xlabel('Range')
    plt.ylabel('Memory Access Frequency')
    plt.title('Distribution of Heatness')
    output_dist = "/home/cc/functions/run_bench/playground/gif/temperatur_distribution.png"
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
    # print("cdf_split raw is: ", cdf_split_raw_temp)
    mask = filtered_sorted_df['temp'] > cdf_split_raw_temp
    cdf_thresh_chunk = filtered_sorted_df[mask]
    return cdf_thresh_chunk

# Given the heatness of the none-zero, sorted df, plot the cdf of heatness
def plot_heatness_cdf(filtered_sorted_temp):
    cdf_y = np.arange(1, len(filtered_sorted_temp) + 1) / len(filtered_sorted_temp)
    plt.plot(filtered_sorted_temp, cdf_y, linestyle='-', color='red')
    plt.xlabel('Memory Access Frequency')
    plt.ylabel('CDF')
    plt.title('CDF of heatness of gif')
    plt.grid(False)
    output_cdf = "/home/cc/functions/run_bench/playground/gif/heat_cdf.png"
    plt.savefig(output_cdf)

def get_heatness_thresh_chunk(filtered_sorted_df, temp_split_percent=0.8):
    largest_temp = filtered_sorted_df['temp'].iloc[-1]
    # print("largest temp:", largest_temp)
    temp_split_value = (temp_split_percent * largest_temp)
    # print("temp_split_value: ", temp_split_value)
    # differences = np.abs(filtered_sorted_df['temp'] - temp_split_value)
    # closest_index = differences.idxmin()
    # heatness_split_raw_temp = filtered_sorted_df.loc[closest_index]['temp']
    mask = filtered_sorted_df['temp'] > temp_split_value
    heatness_thresh_chunk = filtered_sorted_df[mask]
    return heatness_thresh_chunk


def main():
    abs_all = pd.read_csv('/home/cc/functions/run_bench/playground/gif/abs_addr_time.txt', sep='\t', names=['abs_time', 'abs_addr', 'temp'])
    sorted_abs_all = abs_all.sort_values(by='temp')
    # print(sorted_abs_all)
    filtered_sorted_all = sorted_abs_all[sorted_abs_all['temp'] != 0.0]

    plot_heatness_cdf(filtered_sorted_all['temp'])
    plot_heatness_dist(filtered_sorted_all['temp'])
    cdf_chunk = get_cdf_thresh_chunk(filtered_sorted_all, 0.8)
    # heatness_chunk = get_heatness_thresh_chunk(filtered_sorted_all, 0.8)
    print(cdf_chunk)
    
    # profile mmap call stack
    # TODO: modify porter_lib, comma, strict row elem representation
    # call_stack_df = pd.read_csv('/home/cc/functions/run_bench/playground/gif/intecepted.log', sep=', ', names=['timestamp', 'syscall', 'addr_dec', 'addr_hex', 'size'])
    # # call_stack_df = call_stack_df[call_stack_df.apply(lambda row: len(row) > 4, axis=1)]
    # mmap_df = call_stack_df[call_stack_df['syscall'] == 'mmap']
    # print(mmap_df)


    


main()
