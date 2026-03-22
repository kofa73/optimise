perf: Skip redundant cross-corner array calculations for fully isotropic paths

The `LF_cross` and `HF_cross` aligned pixel arrays are computed unconditionally for every pixel, requiring memory writes and arithmetic subtractions. However, these diagonal cross arrays are strictly ignored by the `DT_ISOTROPY_ISOTROPE` convolution logic. By wrapping their assignments in a compile-time macro check for `(!GRAD_ISOTROPIC || !LAPL_ISOTROPIC)`, we completely eliminate dead vector arithmetic and stack array writes during isotropic diffusion passes without introducing new dynamic branches.
outcome: target not reached: 207.366s vs baseline 206.974s (-0.2%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.907 | 6.014 |
| 51.476 | 593.735 |
| 4.132 | 42.744 |
| 12.460 | 137.641 |
| 12.517 | 138.485 |
| 20.575 | 237.625 |
| 13.735 | 156.652 |
| 17.098 | 197.236 |
| 12.380 | 138.643 |
| 15.415 | 176.573 |
| 10.404 | 117.279 |
| 4.465 | 47.565 |
| 1.460 | 10.937 |
| 6.939 | 73.879 |
| 13.464 | 150.310 |
| 0.881 | 6.486 |
| 0.708 | 5.188 |
| 1.294 | 9.453 |
| 1.808 | 16.815 |
| 3.226 | 33.921 |
| 2.022 | 18.909 |

# Totals
| user | cpu |
| ---- | ---- |
| 207.366 | 2316.090 |

# Averages
| user | cpu |
| ---- | ---- |
| 9.875 | 110.290 |
