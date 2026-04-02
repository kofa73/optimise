perf: add a compact two-order pixel body for first-and-fourth-only diffusion

Introduce an always-inline pixel helper for the common case where only the 1st and 4th orders survive after scale setup. Keep just two derivative accumulators and the variance accumulator live, and fold their weighted sum directly into the final update instead of carrying generic four-entry derivative/kernel state through the whole body. That should reduce register pressure without resorting to the broad loop fusion patterns that previously regressed.
outcome: target not reached: 163.495s vs baseline 163.012s (-0.3%, need 3.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.690 | 61.231 |
| 9.463 | 106.581 |
| 9.026 | 101.623 |
| 9.303 | 102.894 |
| 9.219 | 103.044 |
| 9.143 | 103.658 |
| 8.740 | 101.160 |
| 9.025 | 103.236 |
| 0.040 | 0.257 |
| 9.868 | 111.334 |
| 9.522 | 109.381 |
| 9.128 | 103.658 |
| 6.396 | 68.940 |
| 9.704 | 107.871 |
| 9.479 | 105.800 |
| 5.406 | 60.113 |
| 5.427 | 60.937 |
| 6.451 | 69.497 |
| 7.174 | 81.770 |
| 8.389 | 96.167 |
| 6.902 | 75.837 |

# Totals
| user | cpu |
| ---- | ---- |
| 163.495 | 1834.989 |

# Averages
| user | cpu |
| ---- | ---- |
| 7.785 | 87.380 |
