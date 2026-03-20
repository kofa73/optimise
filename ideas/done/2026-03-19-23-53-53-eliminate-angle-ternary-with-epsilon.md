perf: eliminate angle calculation conditionals by adding a tiny epsilon

To prevent division by zero when calculating angles, the code currently utilizes SIMD-disrupting ternary conditionals (`magnitude != 0.f ? ... : 1.f`). Since a zero magnitude implies an absolutely flat region where orientation theoretically doesn't matter (as long as `cos² + sin² = 1` is preserved), we can simply add a tiny, non-underflowing epsilon (`1e-15f`) to `grad_x` and `lapl_x` prior to the magnitude calculation. This guarantees a non-zero hypotenuse, forces perfect defaults, and completely eliminates the ternary branches.
outcome: benchmark early abort: Benchmark early abort: 222.252s vs baseline 217.223s (-2.3%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.943 | 6.333 |
| 57.251 | 640.374 |
| 4.437 | 46.359 |
| 13.028 | 142.310 |
| 12.986 | 142.134 |
| 21.927 | 250.674 |
| 14.444 | 166.977 |
| 18.339 | 208.705 |
| 12.621 | 137.979 |
| 16.255 | 188.046 |
| 11.301 | 124.392 |
| 4.722 | 51.272 |
| 1.508 | 11.549 |
| 7.324 | 79.292 |
| 14.301 | 159.376 |
| 0.953 | 7.293 |
| 0.776 | 5.726 |
| 1.326 | 9.875 |
| 1.941 | 18.766 |
| 3.661 | 36.820 |
| 2.208 | 20.531 |

# Totals
| user | cpu |
| ---- | ---- |
| 222.252 | 2454.783 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.583 | 116.894 |
