Skip all per-pixel work for diffusion orders with zero speed

When a diffusion speed parameter (first/second/third/fourth) is zero, the corresponding ABCD coefficient is zero and that order contributes nothing to the result. Currently the code still computes gradients, exp(c2), rotation matrices, kernels, and convolutions for these zero-contribution orders at every pixel. By checking which ABCD values are nonzero before entering the pixel loop (once per scale, not per pixel), we can skip the gradient normalization, dt_vector_exp, compute_kernel, and convolution for dead orders. Many presets set 1-2 speeds to zero (e.g., denoise sets second=fourth=0), which would eliminate 25-50% of per-pixel computation.

outcome: benchmark early abort: Benchmark early abort: 396.242s vs baseline 217.223s (-82.4%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.897 | 6.192 |
| 105.059 | 1215.034 |
| 7.932 | 88.022 |
| 26.089 | 293.813 |
| 25.916 | 294.672 |
| 37.815 | 441.688 |
| 25.542 | 292.799 |
| 31.588 | 368.497 |
| 12.509 | 138.650 |
| 29.653 | 345.299 |
| 20.013 | 230.083 |
| 8.389 | 95.695 |
| 2.631 | 25.104 |
| 15.162 | 167.817 |
| 28.401 | 325.037 |
| 1.488 | 14.062 |
| 1.192 | 11.044 |
| 2.455 | 20.108 |
| 3.336 | 35.312 |
| 6.370 | 71.499 |
| 3.805 | 40.023 |

# Totals
| user | cpu |
| ---- | ---- |
| 396.242 | 4520.450 |

# Averages
| user | cpu |
| ---- | ---- |
| 18.869 | 215.260 |
