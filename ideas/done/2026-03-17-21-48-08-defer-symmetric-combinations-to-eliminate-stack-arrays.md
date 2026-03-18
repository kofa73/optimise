perf: Defer symmetric pixel combinations to accumulation loop to eliminate stack arrays

The pixel loop currently computes and stores 10 `dt_aligned_pixel_t` arrays for symmetric combinations (e.g., `LF_cross`, `HF_sum_corners`) before the `dt_vector_exp` barrier, forcing over 160 bytes of register spilling to the stack per pixel. By fetching only the direct neighbors needed for gradients in the first pass, and deferring the full 3x3 neighborhood fetches and symmetric math until after the exponential barrier, these combinations can be computed as pure scalars directly inside the accumulation loop. This relies on fast L1 cache hits for the re-fetched pixels to entirely eliminate the massive stack allocation overhead without altering the floating-point operation sequence.
outcome: benchmark early abort: Benchmark early abort: 416.348s vs baseline 217.223s (-91.7%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.624 | 13.114 |
| 109.052 | 1257.757 |
| 8.231 | 91.546 |
| 26.822 | 302.089 |
| 26.501 | 302.637 |
| 40.975 | 472.145 |
| 29.760 | 321.612 |
| 34.207 | 393.413 |
| 12.292 | 142.351 |
| 30.798 | 352.700 |
| 20.620 | 237.612 |
| 8.724 | 97.233 |
| 2.816 | 27.458 |
| 15.104 | 167.408 |
| 30.099 | 343.249 |
| 1.496 | 14.072 |
| 1.168 | 10.909 |
| 2.395 | 22.903 |
| 3.466 | 34.951 |
| 6.385 | 71.009 |
| 3.813 | 40.425 |

# Totals
| user | cpu |
| ---- | ---- |
| 416.348 | 4716.593 |

# Averages
| user | cpu |
| ---- | ---- |
| 19.826 | 224.600 |
