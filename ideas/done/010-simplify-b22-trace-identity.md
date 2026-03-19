compute central laplacian weight directly using matrix trace identity

In the `build_matrix` function, the central weight `b22` is computed as `-2.0f * (a[0][0] + a[1][1])`. Since `a` is derived from an anisotropically scaled rotation matrix, its trace `(a[0][0] + a[1][1])` mathematically simplifies to exactly `1.0f + c2` in all anisotropic modes (because `cos²θ + sin²θ = 1`). By substituting this universal trigonometric identity, we can compute `b22 = -2.0f * (1.0f + c2)` directly. This mathematical simplification eliminates an unnecessary addition instruction per channel and reduces the critical path dependency on the `a[0][0]` and `a[1][1]` computations.

outcome: benchmark early abort: Benchmark early abort: 222.788s vs baseline 217.223s (-2.6%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.952 | 6.394 |
| 56.014 | 647.892 |
| 4.450 | 47.318 |
| 12.946 | 147.098 |
| 13.119 | 147.046 |
| 22.325 | 257.176 |
| 14.997 | 170.998 |
| 18.624 | 213.491 |
| 12.297 | 142.388 |
| 16.950 | 192.914 |
| 11.189 | 128.828 |
| 5.097 | 52.071 |
| 1.521 | 12.024 |
| 7.295 | 79.919 |
| 14.494 | 161.128 |
| 0.901 | 7.094 |
| 0.722 | 5.421 |
| 1.389 | 10.546 |
| 1.930 | 18.751 |
| 3.443 | 37.287 |
| 2.133 | 20.610 |

# Totals
| user | cpu |
| ---- | ---- |
| 222.788 | 2506.394 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.609 | 119.352 |
