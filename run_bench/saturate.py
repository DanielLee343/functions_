import time
import numpy as np
import threading

# Allocate two large arrays of floats
num_elements = 10_000_000  # 10 million floats
data1 = np.ones(num_elements, dtype=np.float32)
data2 = np.ones(num_elements, dtype=np.float32)

# Define a function that reads and writes the entire array
num_iterations = 1000
def memory_bandwidth_test(data):
    for i in range(num_iterations):
        # Read the entire array
        total = np.sum(data)

        # Write to the entire array
        data += 1.0

# Create two threads that run the memory_bandwidth_test() function
threads_list = []
for t in range(2):
    thread = threading.Thread(target=memory_bandwidth_test, args=(np.ones(num_elements, dtype=np.float32),))
    threads_list.append(thread)
    # thread2 = threading.Thread(target=memory_bandwidth_test, args=(data2,))

# Start the threads and measure the elapsed time
start_time = time.monotonic()
for each_thread in threads_list:
    each_thread.start()
# thread1.start()
# thread2.start()
for each_thread in threads_list:
    each_thread.join()
# thread1.join()
# thread2.join()
end_time = time.monotonic()
elapsed_time = end_time - start_time

# Compute the memory bandwidth in GB/s
bytes_processed = 2 * num_iterations * num_elements * 4  # 4 bytes per float
bandwidth = bytes_processed / elapsed_time / 1e9
print(f"Memory bandwidth: {bandwidth:.2f} GB/s")
