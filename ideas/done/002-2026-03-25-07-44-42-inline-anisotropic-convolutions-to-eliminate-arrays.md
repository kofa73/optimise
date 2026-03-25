perf: directly inline anisotropic convolutions to eliminate array materialization

While the isotropic convolution path has been directly inlined to great success, the anisotropic paths still call the generalized `accumulate_convolution_direct` inline function. Because this function signature demands `dt_aligned_pixel_t` arrays for parameters like `cross_corners` and `sum_tb`, the compiler cannot transparently scalarize them and must physically materialize these intermediate symmetric combinations into memory before the call. By explicitly inlining the algebraic formulas for both `DT_ISOTROPY_ISOPHOTE` and `DT_ISOTROPY_GRADIENT` directly inside the `DIFFUSE_PIXEL_BODY`, we sever the array-passing dependency entirely, allowing the compiler to retain all symmetric combinations strictly in registers.
outcome: target not reached: 173.740s vs baseline 172.940s (-0.5%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.644 | 61.036 |
| 9.277 | 104.962 |
| 8.768 | 97.292 |
| 9.096 | 101.506 |
| 9.143 | 101.217 |
| 8.875 | 100.365 |
| 8.507 | 98.261 |
| 8.702 | 100.263 |
| 9.746 | 110.101 |
| 9.845 | 112.218 |
| 9.597 | 110.473 |
| 9.108 | 104.709 |
| 6.369 | 68.192 |
| 9.330 | 104.932 |
| 9.658 | 107.137 |
| 5.802 | 64.825 |
| 5.830 | 65.878 |
| 6.324 | 68.509 |
| 7.733 | 87.962 |
| 8.984 | 103.772 |
| 7.402 | 82.398 |

# Totals
| user | cpu |
| ---- | ---- |
| 173.740 | 1956.008 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.273 | 93.143 |
