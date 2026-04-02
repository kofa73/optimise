perf: specialize third-fourth-order isophote CPU helper to accept third-order-only presets

The existing `heat_PDE_diffusion_no_mask_zero_sharpness_third_fourth_isophote` fast path currently enforces a strict gate requiring both the 3rd and 4th diffusion orders to be active (`ABCD[3] != 0.f` and `isotropy_type[3] == DT_ISOTROPY_ISOPHOTE`). By relaxing this conditional gate to also allow `ABCD[3] == 0.f` (treating an inactive 4th order as functionally matching the isophote requirements), third-order-only presets can utilize this highly optimized path. Since `ABCD[3]` is strictly zero, any 4th-order isophote math performed by the helper is safely multiplied by zero during accumulation. This directly optimizes the target preset by preventing it from falling back to the much slower, generic multi-order CPU loop.
outcome: improvement
commit: 38e665f955
Reduced instance 12 time from 6.449s to 5.957s (+7.6% improvement), reduced sum(user) from 159.078s to 158.077s (~+0.6% improvement)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.706 | 61.585 |
| 8.405 | 93.062 |
| 7.288 | 80.584 |
| 9.276 | 103.055 |
| 9.312 | 103.114 |
| 9.094 | 103.802 |
| 8.772 | 100.246 |
| 8.976 | 102.529 |
| 0.040 | 0.256 |
| 9.808 | 112.071 |
| 9.668 | 109.411 |
| 9.109 | 104.367 |
| 5.957 | 63.378 |
| 9.691 | 108.105 |
| 8.533 | 94.100 |
| 5.545 | 60.384 |
| 5.529 | 61.582 |
| 6.064 | 65.393 |
| 6.665 | 75.069 |
| 7.780 | 88.073 |
| 6.859 | 76.293 |

# Totals
| user | cpu |
| ---- | ---- |
| 158.077 | 1766.459 |

# Averages
| user | cpu |
| ---- | ---- |
| 7.527 | 84.117 |
