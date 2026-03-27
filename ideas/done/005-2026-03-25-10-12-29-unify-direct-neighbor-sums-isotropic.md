perf: unify top-bottom and left-right sums into a single direct-neighbor sum for isotropic paths

For fully isotropic diffusion presets, the horizontal and vertical neighbor sums (`sum_tb` and `sum_lr`) are always applied symmetrically with identical weights (0.5f) to form the isotropic base, and are never used independently to compute directional corrections. By pre-adding them into a single `sum_direct = lf1 + lf3 + lf5 + lf7` variable immediately inside the pixel body, we eliminate the need to store and manipulate `tb` and `lr` independently. This reduces local variable tracking and saves a vector addition per channel in the main convolution accumulation.
outcome: benchmark early abort: Benchmark early abort: 186.637s vs baseline 172.940s (-7.9%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 6.366 | 60.911 |
| 9.990 | 102.772 |
| 9.435 | 96.730 |
| 10.599 | 101.074 |
| 9.734 | 103.763 |
| 9.750 | 101.124 |
| 9.391 | 97.850 |
| 9.411 | 100.987 |
| 10.285 | 107.443 |
| 10.228 | 111.775 |
| 10.017 | 109.226 |
| 9.285 | 104.559 |
| 6.535 | 68.953 |
| 9.933 | 104.118 |
| 10.597 | 106.220 |
| 6.467 | 63.448 |
| 6.055 | 65.441 |
| 6.735 | 68.526 |
| 8.421 | 88.431 |
| 9.709 | 104.481 |
| 7.694 | 82.699 |

# Totals
| user | cpu |
| ---- | ---- |
| 186.637 | 1950.531 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.887 | 92.882 |
