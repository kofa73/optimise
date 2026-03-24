perf: eliminate intermediate blur stack array in B-spline decomposition

In `decompose_2D_Bspline_diffuse`, the horizontal B-spline pass writes its output into a local `dt_aligned_pixel_t blur` stack array, which is then copied channel-by-channel into the `LF` memory buffer. We can eliminate this intermediate stack allocation and the redundant memory copy loop entirely by passing `LF + index` directly as the destination pointer to `_bspline_horizontal`. Since the inline function only writes its final accumulated result once at the end, this safely stores the result directly in the destination memory. The high-frequency detail calculation can then simply read `LF[index + c]`, which is guaranteed to be an immediate L1 cache hit.
outcome: target not reached: 175.981s vs baseline 175.941s (-0.0%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.624 | 60.957 |
| 9.369 | 106.006 |
| 9.038 | 100.130 |
| 9.208 | 102.875 |
| 9.285 | 103.006 |
| 9.041 | 103.407 |
| 8.702 | 100.750 |
| 8.916 | 101.880 |
| 9.745 | 109.905 |
| 9.806 | 110.920 |
| 9.502 | 109.222 |
| 9.125 | 103.751 |
| 6.344 | 68.208 |
| 9.573 | 107.744 |
| 9.827 | 109.506 |
| 5.890 | 65.904 |
| 5.923 | 67.142 |
| 6.355 | 68.908 |
| 7.932 | 91.023 |
| 9.245 | 106.878 |
| 7.531 | 83.972 |

# Totals
| user | cpu |
| ---- | ---- |
| 175.981 | 1982.094 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.380 | 94.385 |
