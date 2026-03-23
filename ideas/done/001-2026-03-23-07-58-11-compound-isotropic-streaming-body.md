perf: rewrite fully-isotropic pixel body as single streaming computation without intermediate arrays

In the fully-isotropic (GRAD_ISOTROPIC=1, LAPL_ISOTROPIC=1) macro expansion, rewrite the entire pixel body so that the isotropic Laplacian accumulation, variance computation, and final integration happen in a single for_each_channel pass directly during neighbor loads, eliminating ~10 intermediate dt_aligned_pixel_t stack arrays (LF_cross, LF_sum_corners, LF_sum_tb, LF_sum_lr, LF_center, and all HF equivalents, plus variance and acc). Pre-compute per-scale constants ABCD_LF=ABCD[0]+ABCD[1] and ABCD_HF=ABCD[2]+ABCD[3] outside the pixel loop. Each channel iteration loads 9 LF and 9 HF values, accumulates the weighted isotropic Laplacian directly (avoiding storing/reloading intermediate sums), computes variance inline, and writes the final result in one pass. Individual sub-optimizations in this list (paired ABCD, merged variance, eliminated center arrays) each showed ~0% improvement alone, but the learnings show compounding structurally related near-miss optimizations that all reduce the same bottleneck (stack pressure/register spilling) successfully compounds to meaningful gains (~6%).
outcome: target not reached: 186.811s vs baseline 186.625s (-0.1%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.711 | 61.454 |
| 10.599 | 116.516 |
| 8.961 | 99.717 |
| 10.054 | 110.149 |
| 9.990 | 110.907 |
| 10.332 | 116.619 |
| 9.875 | 113.109 |
| 10.058 | 115.264 |
| 9.882 | 109.835 |
| 9.952 | 113.051 |
| 9.827 | 110.947 |
| 9.284 | 105.299 |
| 6.630 | 70.356 |
| 9.699 | 107.649 |
| 9.894 | 109.343 |
| 6.718 | 73.674 |
| 6.688 | 75.104 |
| 6.646 | 71.563 |
| 8.117 | 91.426 |
| 9.422 | 107.611 |
| 8.472 | 93.873 |

# Totals
| user | cpu |
| ---- | ---- |
| 186.811 | 2083.466 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.896 | 99.213 |
