perf: statically constant-fold boundary coordinates in peeled left/right PDE column loops

The previous column loop peeling optimization successfully isolated the boundary pixels from the main center loop, but it left the dynamic `MAX(j - col_step, 0)` and `MIN(j + col_step, width - 1)` bounds as arguments in the peeled left and right edge loops. Since `j < col_step` is strictly guaranteed in the left loop, `j_left` will always evaluate to `0`. Similarly, `j_right` will always evaluate to `width - 1` in the right loop. By explicitly replacing the MIN/MAX arguments with the constants `0` and `width - 1` in the peeled function calls, we eliminate the remaining redundant runtime clamping ALUs for boundary pixels, which can make up to ~17% of the image on coarse wavelet scales.
outcome: benchmark early abort: Benchmark early abort: 167.596s vs baseline 163.578s (-2.5%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.948 | 61.236 |
| 9.434 | 106.012 |
| 9.088 | 102.116 |
| 9.482 | 102.644 |
| 9.284 | 103.157 |
| 9.349 | 102.737 |
| 8.646 | 99.751 |
| 9.196 | 101.670 |
| 0.040 | 0.249 |
| 9.747 | 111.149 |
| 9.519 | 109.099 |
| 9.393 | 103.480 |
| 6.820 | 69.459 |
| 11.156 | 109.353 |
| 9.944 | 111.106 |
| 5.469 | 60.389 |
| 5.765 | 60.818 |
| 6.447 | 69.712 |
| 7.259 | 82.489 |
| 8.710 | 96.188 |
| 6.900 | 76.484 |

# Totals
| user | cpu |
| ---- | ---- |
| 167.596 | 1839.298 |

# Averages
| user | cpu |
| ---- | ---- |
| 7.981 | 87.586 |
