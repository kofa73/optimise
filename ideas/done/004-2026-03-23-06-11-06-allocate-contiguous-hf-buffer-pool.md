perf: allocate all effective HF scale buffers as a single contiguous memory pool

Currently, `HF` wavelet detail buffers are allocated individually using a loop that calls `dt_alloc_align_float` up to `MAX_NUM_SCALES` times. We can replace this loop with a single allocation of one large contiguous memory block (`width * height * 4 * effective_scales`) and simply partition the pointers for each `HF[s]`. This minimizes allocator overhead, guarantees a tightly packed memory layout to reduce virtual memory fragmentation, and slightly improves TLB locality when the PDE solver shifts between scales.
outcome: benchmark early abort: Benchmark early abort: 196.051s vs baseline 186.625s (-5.1%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.989 | 62.780 |
| 10.771 | 117.999 |
| 9.462 | 100.019 |
| 10.245 | 111.458 |
| 10.395 | 110.574 |
| 10.722 | 117.986 |
| 10.451 | 114.329 |
| 10.790 | 117.525 |
| 10.440 | 110.803 |
| 10.148 | 113.953 |
| 10.179 | 111.448 |
| 10.282 | 108.415 |
| 6.800 | 71.088 |
| 10.318 | 107.877 |
| 10.771 | 111.857 |
| 7.334 | 74.534 |
| 7.764 | 76.816 |
| 6.889 | 72.029 |
| 8.444 | 91.567 |
| 9.414 | 107.449 |
| 8.443 | 94.285 |

# Totals
| user | cpu |
| ---- | ---- |
| 196.051 | 2104.791 |

# Averages
| user | cpu |
| ---- | ---- |
| 9.336 | 100.228 |
