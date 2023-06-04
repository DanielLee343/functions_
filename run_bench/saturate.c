#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>

#define N (1 << 28) // 256 MB
#define ITERATIONS 100

int main(void) {
    // Allocate memory
    uint8_t *data = (uint8_t *) malloc(N);
    if (data == NULL) {
        fprintf(stderr, "Failed to allocate memory\n");
        return 1;
    }

    // Initialize memory
    for (size_t i = 0; i < N; i++) {
        data[i] = (uint8_t) (i % 256);
    }

    // Measure memory bandwidth
    double start_time = (double) clock() / CLOCKS_PER_SEC;
    for (int i = 0; i < ITERATIONS; i++) {
        for (size_t j = 0; j < N; j++) {
            data[j]++;
        }
    }
    double end_time = (double) clock() / CLOCKS_PER_SEC;

    // Compute memory bandwidth
    double elapsed_time = end_time - start_time;
    size_t bytes_processed = ITERATIONS * N;
    double bandwidth = bytes_processed / elapsed_time / (1 << 30); // GB/s
    printf("Memory bandwidth: %.2f GB/s\n", bandwidth);

    // Free memory
    free(data);

    return 0;
}
