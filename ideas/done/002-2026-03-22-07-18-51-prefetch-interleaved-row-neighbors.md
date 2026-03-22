perf: add software prefetch hints for non-sequential row access in PDE solver

Add `__builtin_prefetch` hints at the start of each row iteration in `heat_PDE_diffusion` (within the DIFFUSE_ROW_LOOP macro) to prefetch the LF and HF data for the next row's three neighbor bands (i-mult, i, i+mult). The `dwt_interleave_rows` function maps consecutive loop iterations to non-adjacent physical rows (e.g., rows 0, stride, 2*stride, ..., then 1, stride+1, ...), creating a strided access pattern that completely defeats the hardware prefetcher. For large images where each row is ~80KB (5000px × 4ch × 4B), the three neighbor rows span ~240KB of non-contiguous memory, far exceeding L1 cache. By issuing prefetch instructions for the next iteration's row offsets while the current pixel computation is in flight, we can overlap memory fetch latency (100-300 cycles for LLC/DRAM) with the substantial per-pixel arithmetic.
outcome: benchmark early abort: Benchmark early abort: 219.307s vs baseline 206.974s (-6.0%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.968 | 6.462 |
| 53.650 | 601.546 |
| 4.410 | 44.046 |
| 12.930 | 141.380 |
| 13.183 | 140.714 |
| 22.136 | 244.171 |
| 14.815 | 161.362 |
| 18.477 | 203.437 |
| 12.392 | 142.349 |
| 16.714 | 182.514 |
| 11.143 | 121.974 |
| 4.970 | 48.910 |
| 1.545 | 11.409 |
| 7.312 | 76.209 |
| 14.130 | 152.596 |
| 0.915 | 6.893 |
| 0.753 | 5.497 |
| 1.402 | 10.134 |
| 1.879 | 17.703 |
| 3.439 | 35.282 |
| 2.144 | 19.464 |

# Totals
| user | cpu |
| ---- | ---- |
| 219.307 | 2374.052 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.443 | 113.050 |
