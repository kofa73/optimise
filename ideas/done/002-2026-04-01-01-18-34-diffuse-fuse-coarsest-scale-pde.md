perf: consume the coarsest wavelet detail immediately after decomposition

In `wavelets_process`, special-case the last `decompose_2D_Bspline()` iteration so the coarsest `HF[scales - 1]` is fed straight into the first CPU `heat_PDE_diffusion()` step instead of being written out, parked, then read back in the reconstruction loop. The coarsest scale has the longest reuse distance and sits at the top of a max-scale run for this preset, so deleting that full-frame write/read round-trip should pay back better than small ALU tweaks.
outcome: benchmark early abort: Benchmark early abort: 167.316s vs baseline 163.578s (-2.3%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.686 | 62.383 |
| 9.471 | 107.095 |
| 9.382 | 102.193 |
| 9.274 | 103.535 |
| 9.563 | 103.095 |
| 9.235 | 106.061 |
| 9.252 | 104.788 |
| 9.184 | 105.349 |
| 0.039 | 0.255 |
| 9.957 | 113.536 |
| 9.997 | 111.074 |
| 9.190 | 105.545 |
| 6.668 | 68.620 |
| 9.728 | 109.536 |
| 9.947 | 111.424 |
| 5.749 | 60.544 |
| 5.505 | 62.094 |
| 6.425 | 70.076 |
| 7.596 | 83.213 |
| 8.560 | 98.627 |
| 6.908 | 77.060 |

# Totals
| user | cpu |
| ---- | ---- |
| 167.316 | 1866.103 |

# Averages
| user | cpu |
| ---- | ---- |
| 7.967 | 88.862 |
