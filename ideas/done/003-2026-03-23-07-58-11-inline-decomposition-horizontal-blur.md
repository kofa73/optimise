perf: inline horizontal blur in decomposition to fuse blur/LF-write/HF-subtract into one pass

In decompose_2D_Bspline_diffuse, the inner column loop calls _bspline_horizontal into a local `blur` array, stores blur to LF, computes `detail = in - blur` into another local array, then nontemporal-stores detail to HF. Inline the 5-tap horizontal filter directly and fuse all three operations into a single for_each_channel loop: compute the blur scalar, write it to LF, subtract from input, and accumulate into the nontemporal store buffer — all without the intermediate `blur` and `detail` dt_aligned_pixel_t arrays. This eliminates 2 stack arrays (8 floats) and their store-load forwarding latency, following the proven "replace intermediate stack arrays with native scalar variables" pattern that yielded the largest consistent gains (~6-12%). The decomposition runs for every pixel at every scale at every iteration, so even small per-pixel savings compound.
outcome: benchmark early abort: Benchmark early abort: 188.636s vs baseline 181.409s (-4.0%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.941 | 61.108 |
| 10.321 | 117.539 |
| 9.195 | 99.843 |
| 9.897 | 111.315 |
| 9.854 | 110.645 |
| 9.801 | 108.790 |
| 9.126 | 105.981 |
| 10.438 | 108.846 |
| 10.729 | 110.216 |
| 10.901 | 112.472 |
| 9.947 | 111.398 |
| 10.607 | 104.991 |
| 6.731 | 69.060 |
| 9.584 | 108.072 |
| 10.087 | 109.990 |
| 6.537 | 73.646 |
| 6.805 | 74.498 |
| 6.336 | 68.916 |
| 7.905 | 90.645 |
| 9.604 | 106.882 |
| 8.290 | 93.784 |

# Totals
| user | cpu |
| ---- | ---- |
| 188.636 | 2058.637 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.983 | 98.030 |
