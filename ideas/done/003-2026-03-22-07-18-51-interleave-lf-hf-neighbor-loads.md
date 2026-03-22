perf: interleave LF and HF neighbor loads to maximize memory-level parallelism

Restructure the `for_each_channel` loop in the DIFFUSE_PIXEL_BODY macro to interleave LF and HF neighbor loads instead of loading all 9 LF values first then all 9 HF values. Currently, the 9 HF loads begin only after all 9 LF loads and their combination computations complete, meaning the first HF cache miss doesn't issue until ~50+ instructions into the loop body — potentially beyond the CPU's out-of-order window. By interleaving loads as `lf0=LF[n0+c]; hf0=HF[n0+c]; lf1=LF[n1+c]; hf1=HF[n1+c]; ...` (with combination computations deferred until all loads are issued), the memory controller can begin fetching from both arrays simultaneously, doubling effective memory bandwidth utilization. The symmetric combination and angle computations would follow using the already-loaded scalar values. This reorganization preserves identical computation and results while better exploiting the CPU's multiple load ports and outstanding memory request capacity.
outcome: benchmark early abort: Benchmark early abort: 214.166s vs baseline 206.974s (-3.5%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.923 | 6.098 |
| 52.827 | 604.591 |
| 4.219 | 43.913 |
| 12.983 | 142.181 |
| 12.959 | 142.735 |
| 21.428 | 244.321 |
| 14.141 | 163.200 |
| 17.905 | 203.140 |
| 12.513 | 139.368 |
| 15.910 | 183.283 |
| 11.009 | 120.930 |
| 4.618 | 50.172 |
| 1.486 | 11.306 |
| 7.102 | 76.461 |
| 13.999 | 153.835 |
| 0.898 | 6.749 |
| 0.731 | 5.435 |
| 1.301 | 9.514 |
| 1.828 | 17.572 |
| 3.285 | 35.002 |
| 2.101 | 19.422 |

# Totals
| user | cpu |
| ---- | ---- |
| 214.166 | 2379.228 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.198 | 113.297 |
