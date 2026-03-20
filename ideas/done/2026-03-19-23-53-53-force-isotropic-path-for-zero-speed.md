perf: force isotropic path for zero-speed orders to leverage existing unswitching

Attempting to skip loop iterations for zero-speed orders creates SIMD-breaking branches. However, when both gradient-driven orders (0 and 2) or both laplacian-driven orders (1 and 3) have speeds of zero (`ABCD == 0.f`), their angles and magnitudes are multiplied by zero anyway. By preemptively overwriting their `isotropy_type` to `DT_ISOTROPY_ISOTROPE` at the top of the function, we cleanly trick the existing `grad_is_isotropic` unswitched macros into routing execution to the faster loop variants, safely bypassing all expensive trig and magnitude math without introducing new macros.
outcome: benchmark early abort: Benchmark early abort: 224.548s vs baseline 217.223s (-3.4%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.899 | 6.101 |
| 57.058 | 658.892 |
| 4.478 | 47.414 |
| 13.241 | 145.663 |
| 13.017 | 146.877 |
| 22.327 | 256.295 |
| 15.018 | 170.055 |
| 18.726 | 213.787 |
| 12.371 | 142.835 |
| 16.835 | 191.305 |
| 11.461 | 127.343 |
| 4.808 | 52.668 |
| 1.522 | 11.794 |
| 7.446 | 80.817 |
| 14.715 | 163.677 |
| 0.917 | 7.296 |
| 0.725 | 5.633 |
| 1.364 | 10.268 |
| 1.938 | 18.999 |
| 3.514 | 37.739 |
| 2.168 | 20.960 |

# Totals
| user | cpu |
| ---- | ---- |
| 224.548 | 2516.418 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.693 | 119.829 |
