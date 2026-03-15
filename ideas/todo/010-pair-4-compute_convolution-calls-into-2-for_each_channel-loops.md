Pair the 4 `compute_convolution` calls into 2 `for_each_channel` loops

Pair the 4 `compute_convolution` calls into 2 `for_each_channel` loops: derivatives 0+2 (sharing gradient angle data, applied to LF and HF sums) and derivatives 1+3 (sharing laplacian angle data, applied to LF and HF sums). Each loop computes 2 derivatives in one pass, halving loop overhead and improving register reuse for shared angle values. Careful (bug danger): using isotropy_type[0] for both derivatives 0 and 2 (and [1] for both 1 and 3). Use correct per-derivative isotropy_type

outcome: benchmark early abort: obvious regression

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.770 | 15.098 |
| 91.400 | 1040.904 |
| 7.172 | 75.711 |
| 22.916 | 253.455 |
| 22.853 | 254.349 |
| 41.362 | 468.401 |
| 27.541 | 311.107 |
| 34.443 | 390.201 |
| 12.661 | 141.406 |
| 30.920 | 349.175 |
| 20.953 | 232.783 |
| 8.852 | 96.618 |
| 2.518 | 22.273 |
| 11.596 | 125.290 |
| 22.782 | 252.503 |
| 1.425 | 12.244 |
| 1.084 | 9.514 |
| 2.226 | 19.774 |
| 3.040 | 30.819 |
| 5.764 | 61.353 |
| 3.566 | 35.383 |

# Totals
| user | cpu |
| ---- | ---- |
| 376.844 | 4198.361 |

# Averages
| user | cpu |
| ---- | ---- |
| 17.945 | 199.922 |
