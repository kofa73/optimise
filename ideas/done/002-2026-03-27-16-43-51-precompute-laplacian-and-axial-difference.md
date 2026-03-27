perf: precompute central Laplacian and axial differences to eliminate accumulation ALU

Currently, `accumulate_convolution_direct` recomputes the `iso_base` (the standard 5-point discrete Laplacian: `sum_lr + sum_tb - 4*center`) and the `sum_lr - sum_tb` axial difference on the fly from raw spatial neighbor sums. By computing `iso_base` and `axial_diff` upfront during the neighbor fetch phase and passing them directly to the accumulator, we save several additions inside the core convolution loop. Crucially, for matched orders, we can sum these derived values (`LF_iso_base + HF_iso_base`) directly, compounding the savings by entirely bypassing the combination of raw individual axis sums.
outcome: benchmark early abort: Benchmark early abort: 200.916s vs baseline 172.940s (-16.2%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 6.758 | 55.717 |
| 11.471 | 98.578 |
| 10.357 | 93.353 |
| 10.217 | 101.115 |
| 11.215 | 97.493 |
| 10.570 | 101.847 |
| 10.518 | 98.414 |
| 9.578 | 102.939 |
| 10.418 | 103.116 |
| 10.504 | 110.812 |
| 10.753 | 107.564 |
| 10.026 | 103.172 |
| 6.900 | 67.951 |
| 10.373 | 103.616 |
| 10.860 | 104.498 |
| 7.278 | 61.329 |
| 7.572 | 62.309 |
| 8.175 | 64.391 |
| 9.118 | 87.037 |
| 10.034 | 103.600 |
| 8.221 | 81.657 |

# Totals
| user | cpu |
| ---- | ---- |
| 200.916 | 1910.508 |

# Averages
| user | cpu |
| ---- | ---- |
| 9.567 | 90.977 |
