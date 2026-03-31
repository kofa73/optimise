perf: prebuild per-scale runtime descriptors across outer iterations

Build a compact descriptor array once before the outer `for(it ...)` loop, containing each scale’s `mult`, `current_radius_square`, `ABCD`, `strength`, and the selected CPU PDE helper, then pass that into `wavelets_process()`. The strong benchmark repeats the same scale setup 20 times, so moving this invariant dispatch/setup work out of the iteration path should tighten the CPU-side control flow without changing the algorithm.
outcome: target not reached: 164.022s vs baseline 163.578s (-0.1%, need 3.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.645 | 61.239 |
| 9.412 | 105.970 |
| 9.126 | 101.086 |
| 9.255 | 102.855 |
| 9.324 | 102.163 |
| 9.107 | 103.995 |
| 8.769 | 100.988 |
| 8.973 | 102.338 |
| 0.040 | 0.256 |
| 9.765 | 111.457 |
| 9.633 | 109.226 |
| 9.110 | 104.164 |
| 6.396 | 68.495 |
| 9.747 | 107.995 |
| 9.892 | 110.471 |
| 5.451 | 59.646 |
| 5.425 | 60.758 |
| 6.421 | 69.230 |
| 7.217 | 81.832 |
| 8.439 | 95.844 |
| 6.875 | 75.956 |

# Totals
| user | cpu |
| ---- | ---- |
| 164.022 | 1835.964 |

# Averages
| user | cpu |
| ---- | ---- |
| 7.811 | 87.427 |
