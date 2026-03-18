Merge variance regularization (`variance[c] = threshold + variance[c] * factor`) into the output loop, computing `var` inline and eliminating a separate `for_each_channel` pass.

The output loop body stays small (1 FMA + division + add + fmax).

outcome: benchmark early abort: Benchmark early abort: 222.336s vs baseline 217.223s (-2.4%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.895 | 6.199 |
| 57.064 | 659.352 |
| 4.490 | 47.560 |
| 12.727 | 144.515 |
| 13.082 | 143.987 |
| 22.021 | 253.825 |
| 14.694 | 167.308 |
| 18.053 | 211.221 |
| 12.509 | 139.000 |
| 16.612 | 189.516 |
| 10.976 | 126.413 |
| 4.703 | 51.909 |
| 1.739 | 11.337 |
| 7.418 | 80.756 |
| 14.834 | 163.471 |
| 0.942 | 7.345 |
| 0.761 | 5.683 |
| 1.304 | 9.924 |
| 1.918 | 18.737 |
| 3.459 | 37.294 |
| 2.135 | 20.618 |

# Totals
| user | cpu |
| ---- | ---- |
| 222.336 | 2495.970 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.587 | 118.856 |
