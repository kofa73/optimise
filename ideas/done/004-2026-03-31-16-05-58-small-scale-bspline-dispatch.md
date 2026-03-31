perf: specialize Bspline decomposition for the finest fixed mult values

Introduce small dedicated CPU helpers for the finest `mult` values that dominate the `radius = 3, radius_center = 0` preset family, such as `mult == 1`, `2`, and `4`, while keeping the generic Bspline path as fallback. Those helpers let the compiler constant-fold offset arithmetic and trim generic loop/setup overhead in `decompose_2D_Bspline()`-driven work that is repeated on every outer iteration for the strong benchmark.
outcome: target not reached: 163.952s vs baseline 163.578s (-0.2%, need 3.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.682 | 60.949 |
| 9.467 | 105.578 |
| 8.998 | 101.024 |
| 9.288 | 102.115 |
| 9.287 | 102.734 |
| 9.124 | 103.032 |
| 8.704 | 100.302 |
| 8.902 | 102.276 |
| 0.040 | 0.252 |
| 9.885 | 111.600 |
| 9.559 | 109.366 |
| 9.182 | 104.019 |
| 6.388 | 68.488 |
| 9.628 | 107.851 |
| 9.964 | 110.034 |
| 5.434 | 59.888 |
| 5.437 | 60.577 |
| 6.432 | 69.323 |
| 7.237 | 82.092 |
| 8.426 | 96.364 |
| 6.888 | 75.874 |

# Totals
| user | cpu |
| ---- | ---- |
| 163.952 | 1833.738 |

# Averages
| user | cpu |
| ---- | ---- |
| 7.807 | 87.321 |
