compute central laplacian weight directly using matrix trace identity

In the `build_matrix` function, the central weight `b22` is computed as `-2.0f * (a[0][0] + a[1][1])`. Since `a` is derived from an anisotropically scaled rotation matrix, its trace `(a[0][0] + a[1][1])` mathematically simplifies to exactly `1.0f + c2` in all anisotropic modes (because `cos²θ + sin²θ = 1`). By substituting this universal trigonometric identity, we can compute `b22 = -2.0f * (1.0f + c2)` directly. This mathematical simplification eliminates an unnecessary addition instruction per channel and reduces the critical path dependency on the `a[0][0]` and `a[1][1]` computations.
outcome: benchmark early abort: obvious regression

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.508 | 11.754 |
| 67.589 | 753.266 |
| 5.608 | 56.985 |
| 17.707 | 191.221 |
| 17.860 | 192.316 |
| 30.650 | 342.108 |
| 20.395 | 225.377 |
| 25.463 | 284.595 |
| 12.695 | 139.860 |
| 23.378 | 255.689 |
| 15.477 | 169.439 |
| 6.706 | 70.532 |
| 2.097 | 16.880 |
| 9.223 | 95.818 |
| 17.946 | 193.377 |
| 1.146 | 8.600 |
| 0.872 | 6.561 |
| 1.880 | 14.841 |
| 2.373 | 21.878 |
| 4.274 | 43.663 |
| 2.537 | 23.998 |

# Totals
| user | cpu |
| ---- | ---- |
| 287.384 | 3118.758 |

# Averages
| user | cpu |
| ---- | ---- |
| 13.685 | 148.512 |
