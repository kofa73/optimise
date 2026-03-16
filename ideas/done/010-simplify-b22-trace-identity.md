compute central laplacian weight directly using matrix trace identity

In the `build_matrix` function, the central weight `b22` is computed as `-2.0f * (a[0][0] + a[1][1])`. Since `a` is derived from an anisotropically scaled rotation matrix, its trace `(a[0][0] + a[1][1])` mathematically simplifies to exactly `1.0f + c2` in all anisotropic modes (because `cos²θ + sin²θ = 1`). By substituting this universal trigonometric identity, we can compute `b22 = -2.0f * (1.0f + c2)` directly. This mathematical simplification eliminates an unnecessary addition instruction per channel and reduces the critical path dependency on the `a[0][0]` and `a[1][1]` computations.

outcome: benchmark early abort: Benchmark early abort: 217.438s vs baseline 217.223s (-0.1%, need 3.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.885 | 6.047 |
| 56.075 | 659.693 |
| 4.397 | 46.840 |
| 12.687 | 144.202 |
| 12.721 | 144.351 |
| 21.462 | 251.477 |
| 14.286 | 167.066 |
| 17.835 | 208.918 |
| 12.246 | 141.797 |
| 16.142 | 188.304 |
| 10.891 | 125.263 |
| 4.647 | 51.331 |
| 1.461 | 11.609 |
| 7.251 | 79.106 |
| 14.230 | 162.105 |
| 0.856 | 6.801 |
| 0.691 | 5.328 |
| 1.281 | 10.001 |
| 1.899 | 18.606 |
| 3.388 | 36.978 |
| 2.107 | 20.500 |

# Totals
| user | cpu |
| ---- | ---- |
| 217.438 | 2486.323 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.354 | 118.396 |
