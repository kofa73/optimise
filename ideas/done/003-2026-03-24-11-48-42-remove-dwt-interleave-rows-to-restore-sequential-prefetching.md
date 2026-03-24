perf: remove dwt_interleave_rows to restore optimal hardware memory prefetching

The outer row loops currently use `dwt_interleave_rows` to process image rows in strided jumps, an old technique originally intended to improve 2D cache locality. However, modern CPU hardware prefetchers are heavily optimized for simple, sequential linear memory access. By jumping across rows, the interleaving defeats L1/L2 linear prefetchers and causes unnecessary cache thrashing. Replacing the interleaved index with a straightforward sequential row loop (`const size_t i = row;`) in both the PDE solver and B-spline decomposition will restore optimal hardware prefetcher behavior and improve memory throughput.
outcome: benchmark early abort: Benchmark early abort: 228.914s vs baseline 175.941s (-30.1%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 9.254 | 98.464 |
| 12.645 | 142.323 |
| 11.706 | 128.408 |
| 13.423 | 146.073 |
| 13.219 | 148.024 |
| 12.599 | 139.572 |
| 9.789 | 111.779 |
| 11.203 | 124.601 |
| 11.048 | 127.742 |
| 13.483 | 149.232 |
| 12.036 | 139.131 |
| 12.023 | 132.111 |
| 9.034 | 98.393 |
| 12.530 | 136.225 |
| 12.756 | 141.705 |
| 7.335 | 77.949 |
| 6.667 | 75.457 |
| 9.370 | 100.673 |
| 8.631 | 98.448 |
| 10.092 | 116.559 |
| 10.071 | 108.772 |

# Totals
| user | cpu |
| ---- | ---- |
| 228.914 | 2541.641 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.901 | 121.031 |
