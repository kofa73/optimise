perf: Specialize fully isotropic pixel body to guarantee dead-code elimination of tensor arrays

The current outer-loop unswitching for isotropic paths relies on the compiler deducing that `isotropy_type[k]` equals `DT_ISOTROPY_ISOTROPE` from the boolean `GRAD_ISOTROPIC` macro parameter to eliminate the `switch` statement in `accumulate_convolution_direct`. When the compiler fails to propagate this across the inline boundary, it cannot dead-code eliminate the 14 heavy anisotropic stack arrays (`c2`, `cos_theta_grad_sq`, etc.), leading to massive L1 traffic. Creating a dedicated, hardcoded `DIFFUSE_PIXEL_BODY_ISOTROPIC` macro that directly computes isotropic convolutions and declares only the minimal `sum_corners` and `sum_cross` variables ensures optimal register allocation and zero dynamic switching.
outcome: target not reached: 207.768s vs baseline 206.974s (-0.4%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.903 | 6.040 |
| 51.912 | 594.295 |
| 4.167 | 42.983 |
| 12.429 | 138.324 |
| 12.451 | 137.447 |
| 20.688 | 236.123 |
| 13.606 | 156.800 |
| 17.156 | 196.810 |
| 12.390 | 138.763 |
| 15.388 | 176.942 |
| 10.383 | 117.381 |
| 4.444 | 47.463 |
| 1.467 | 10.688 |
| 6.947 | 73.705 |
| 13.479 | 150.587 |
| 0.889 | 6.695 |
| 0.718 | 5.151 |
| 1.287 | 9.401 |
| 1.806 | 16.902 |
| 3.238 | 33.847 |
| 2.020 | 18.900 |

# Totals
| user | cpu |
| ---- | ---- |
| 207.768 | 2315.247 |

# Averages
| user | cpu |
| ---- | ---- |
| 9.894 | 110.250 |
