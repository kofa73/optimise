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

outcome: benchmark early abort: Benchmark early abort: 241.798s vs baseline 247.307s (+2.2%, need 5.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.238 | 9.935 |
| 56.232 | 664.450 |
| 4.616 | 49.423 |
| 14.816 | 168.925 |
| 14.860 | 168.790 |
| 25.872 | 304.070 |
| 17.220 | 201.668 |
| 21.529 | 253.219 |
| 12.261 | 141.842 |
| 19.529 | 228.194 |
| 13.088 | 151.345 |
| 5.566 | 62.314 |
| 1.688 | 14.289 |
| 7.589 | 83.497 |
| 15.030 | 170.938 |
| 0.882 | 7.167 |
| 0.697 | 5.504 |
| 1.502 | 12.426 |
| 1.897 | 18.967 |
| 3.513 | 38.412 |
| 2.173 | 21.210 |

# Totals
| user | cpu |
| ---- | ---- |
| 241.798 | 2776.585 |

# Averages
| user | cpu |
| ---- | ---- |
| 11.514 | 132.218 |
