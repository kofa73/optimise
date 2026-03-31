perf: bypass 3x3 variance calculation via inner-loop branch when regularization is zero

For presets where `regularization` is exactly zero (such as "bloom" or "inpaint highlights"), the pixel body unconditionally computes the expensive 9-element sum of squares for the HF variance, only to immediately multiply it by a `regularization_factor` of 0.0. Previous attempts to optimize this used outer-loop unswitching, which likely regressed due to catastrophic instruction cache bloat. By instead wrapping the variance computation inside `diffuse_pixel_body` with a highly predictable, loop-invariant `if (ctx->regularization_factor > 0.f)` check, we bypass ~36 MAC operations per pixel for zero-regularization presets with virtually zero overhead.
outcome: benchmark early abort: Benchmark early abort: 173.709s vs baseline 163.578s (-6.2%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.726 | 61.924 |
| 10.050 | 109.851 |
| 9.304 | 104.782 |
| 10.053 | 108.537 |
| 9.722 | 108.483 |
| 9.895 | 109.409 |
| 9.202 | 106.442 |
| 9.427 | 108.456 |
| 0.039 | 0.253 |
| 10.679 | 118.362 |
| 10.132 | 116.166 |
| 9.955 | 110.345 |
| 6.788 | 73.259 |
| 10.293 | 111.771 |
| 10.183 | 114.003 |
| 5.680 | 62.955 |
| 5.996 | 63.589 |
| 6.816 | 74.198 |
| 7.538 | 85.831 |
| 9.051 | 100.275 |
| 7.180 | 79.793 |

# Totals
| user | cpu |
| ---- | ---- |
| 173.709 | 1928.684 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.272 | 91.842 |
