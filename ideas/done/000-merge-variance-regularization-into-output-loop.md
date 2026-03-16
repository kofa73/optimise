Merge variance regularization (`variance[c] = threshold + variance[c] * factor`) into the output loop, computing `var` inline and eliminating a separate `for_each_channel` pass.

The output loop body stays small (1 FMA + division + add + fmax).

outcome: benchmark early abort: Benchmark early abort: 234.317s vs baseline 231.975s (-1.0%, need 5.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.075 | 8.520 |
| 56.155 | 658.681 |
| 4.485 | 47.479 |
| 14.223 | 161.763 |
| 14.266 | 162.353 |
| 24.761 | 289.888 |
| 16.408 | 192.430 |
| 20.565 | 241.364 |
| 12.243 | 142.116 |
| 18.547 | 216.596 |
| 12.459 | 144.032 |
| 5.298 | 59.293 |
| 1.608 | 13.242 |
| 7.352 | 80.375 |
| 14.416 | 164.214 |
| 0.887 | 7.039 |
| 0.702 | 5.428 |
| 1.421 | 11.606 |
| 1.894 | 18.785 |
| 3.437 | 37.413 |
| 2.115 | 20.587 |

# Totals
| user | cpu |
| ---- | ---- |
| 234.317 | 2683.204 |

# Averages
| user | cpu |
| ---- | ---- |
| 11.158 | 127.772 |
