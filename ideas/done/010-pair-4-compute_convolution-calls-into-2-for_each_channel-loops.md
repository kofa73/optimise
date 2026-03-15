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

outcome: benchmark early abort: Benchmark early abort: 367.701s vs baseline 247.307s (-48.7%, need 5.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.695 | 15.661 |
| 89.547 | 1052.224 |
| 6.912 | 76.677 |
| 22.359 | 257.296 |
| 22.411 | 258.006 |
| 41.195 | 474.569 |
| 26.781 | 313.912 |
| 33.485 | 392.375 |
| 12.259 | 141.935 |
| 30.120 | 351.570 |
| 20.216 | 234.134 |
| 8.543 | 96.934 |
| 2.417 | 22.527 |
| 11.235 | 126.230 |
| 22.315 | 257.084 |
| 1.290 | 11.925 |
| 1.042 | 9.429 |
| 2.154 | 19.896 |
| 2.863 | 30.061 |
| 5.506 | 61.314 |
| 3.356 | 34.585 |

# Totals
| user | cpu |
| ---- | ---- |
| 367.701 | 4238.344 |

# Averages
| user | cpu |
| ---- | ---- |
| 17.510 | 201.826 |
