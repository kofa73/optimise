perf: fuse variance regularization FMA into main neighbor-loading loop to eliminate separate pass

The variance regularization (variance = threshold + variance * factor) is currently computed in a separate for_each_channel loop after the dt_vector_exp calls but before convolution accumulation. Since the regularization depends only on the raw variance (computed during neighbor loading) and scale-constant parameters — and is independent of the dt_vector_exp results — it can be moved to the end of the main neighbor-loading for_each_channel loop body, executing before the exp calls. This eliminates one discrete for_each_channel loop pass (4 iterations of loop overhead) per pixel and keeps the regularized variance result warm in registers for the output integration that follows shortly after. The variance result is consumed only in the final output line (acc/variance), which comes after the convolution accumulation, so moving its computation earlier has no correctness impact.
outcome: benchmark early abort: Benchmark early abort: 196.199s vs baseline 181.409s (-8.2%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 6.013 | 64.159 |
| 11.221 | 119.846 |
| 9.767 | 103.847 |
| 10.741 | 113.500 |
| 10.507 | 113.972 |
| 10.488 | 113.079 |
| 9.890 | 110.376 |
| 10.335 | 111.889 |
| 9.760 | 112.535 |
| 10.662 | 115.863 |
| 10.307 | 113.313 |
| 9.750 | 107.825 |
| 7.100 | 70.776 |
| 10.470 | 111.453 |
| 10.871 | 113.032 |
| 6.973 | 75.134 |
| 6.959 | 75.709 |
| 7.124 | 71.070 |
| 8.471 | 92.705 |
| 9.869 | 108.328 |
| 8.921 | 94.883 |

# Totals
| user | cpu |
| ---- | ---- |
| 196.199 | 2113.294 |

# Averages
| user | cpu |
| ---- | ---- |
| 9.343 | 100.633 |
