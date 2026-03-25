perf: absorb variance threshold and regularization into accumulation loop

The high-frequency variance is currently initialized to zero, summed across 9 neighbor squares, and then updated in a standalone pass via `variance[c] = variance_threshold + variance[c] * regularization_factor`. This isolates the scale-and-shift into a separate dependency barrier. By initializing the variance registers directly to `variance_threshold` before the neighborhood loop, and distributing the `regularization_factor` into the squares as they are accumulated, we completely eliminate the standalone post-processing pass. This tighter algebraic structure reduces iteration overhead and helps the compiler pipeline the operations natively without relying on explicit fast-math approximations.
outcome: benchmark early abort: Benchmark early abort: 176.701s vs baseline 172.940s (-2.2%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.644 | 61.723 |
| 9.416 | 102.392 |
| 8.605 | 96.885 |
| 9.185 | 102.420 |
| 9.291 | 101.832 |
| 8.992 | 103.066 |
| 8.990 | 100.065 |
| 8.913 | 102.851 |
| 9.994 | 110.586 |
| 9.728 | 111.101 |
| 9.504 | 109.204 |
| 9.370 | 103.461 |
| 6.342 | 68.588 |
| 10.087 | 110.066 |
| 10.225 | 110.337 |
| 5.734 | 63.963 |
| 6.049 | 64.469 |
| 6.323 | 68.829 |
| 7.729 | 88.451 |
| 9.339 | 103.678 |
| 7.241 | 81.122 |

# Totals
| user | cpu |
| ---- | ---- |
| 176.701 | 1965.089 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.414 | 93.576 |
