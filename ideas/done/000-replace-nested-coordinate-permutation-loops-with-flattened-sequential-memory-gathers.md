Replace nested coordinate permutation loops initializing `neighbour_pixel` matrix and calculating scalar variance with explicitly flattened sequential memory gathers.

Replace nested coordinate permutation loops initializing `neighbour_pixel` matrix and calculating scalar variance with explicitly flattened sequential memory gathers.


outcome: benchmark early abort: Benchmark early abort: 232.651s vs baseline 231.975s (-0.3%, need 5.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.078 | 8.367 |
| 55.992 | 659.773 |
| 4.376 | 46.536 |
| 14.279 | 161.218 |
| 14.211 | 161.516 |
| 24.468 | 287.314 |
| 16.292 | 190.863 |
| 20.341 | 238.932 |
| 12.240 | 141.882 |
| 18.427 | 215.412 |
| 12.330 | 142.666 |
| 5.242 | 58.700 |
| 1.608 | 13.317 |
| 7.227 | 79.008 |
| 14.233 | 161.994 |
| 0.855 | 6.851 |
| 0.683 | 5.296 |
| 1.418 | 11.493 |
| 1.850 | 18.311 |
| 3.390 | 36.923 |
| 2.111 | 20.559 |

# Totals
| user | cpu |
| ---- | ---- |
| 232.651 | 2666.931 |

# Averages
| user | cpu |
| ---- | ---- |
| 11.079 | 126.997 |
