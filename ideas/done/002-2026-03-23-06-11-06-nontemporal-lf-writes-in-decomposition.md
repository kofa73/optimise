perf: use nontemporal stores for LF writes during B-spline decomposition

In `decompose_2D_Bspline_diffuse`, `LF` (blur) is currently written using normal stores because it is reused as input for the next scale. However, because `LF` is a full-image buffer (often ~96MB for a 24MP image), the first pixels written will have long been evicted from the L3 cache by the time the next scale pass begins reading them. Replacing the normal stores with `copy_pixel_nontemporal(LF + index, blur)` prevents the CPU from performing unnecessary read-for-ownership cache line fetches, directly reducing memory bandwidth just like the existing nontemporal optimization for `HF` buffers.
outcome: benchmark early abort: Benchmark early abort: 315.056s vs baseline 186.625s (-68.8%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 10.283 | 107.511 |
| 16.045 | 172.278 |
| 13.842 | 150.365 |
| 15.388 | 164.607 |
| 15.334 | 164.843 |
| 18.148 | 190.322 |
| 20.299 | 207.052 |
| 19.089 | 198.134 |
| 20.902 | 215.888 |
| 17.076 | 183.777 |
| 17.532 | 185.155 |
| 16.510 | 173.626 |
| 10.260 | 106.831 |
| 14.392 | 157.056 |
| 14.599 | 156.641 |
| 10.526 | 111.721 |
| 11.520 | 118.222 |
| 10.384 | 111.500 |
| 13.814 | 143.715 |
| 16.148 | 168.476 |
| 12.965 | 137.769 |

# Totals
| user | cpu |
| ---- | ---- |
| 315.056 | 3325.489 |

# Averages
| user | cpu |
| ---- | ---- |
| 15.003 | 158.357 |
