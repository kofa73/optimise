Skip all per-pixel work for diffusion orders with zero speed

When a diffusion speed parameter (first/second/third/fourth) is zero, the corresponding ABCD coefficient is zero and that order contributes nothing to the result. Currently the code still computes gradients, exp(c2), rotation matrices, kernels, and convolutions for these zero-contribution orders at every pixel. By checking which ABCD values are nonzero before entering the pixel loop (once per scale, not per pixel), we can skip the gradient normalization, dt_vector_exp, compute_kernel, and convolution for dead orders. Many presets set 1-2 speeds to zero (e.g., denoise sets second=fourth=0), which would eliminate 25-50% of per-pixel computation.
outcome: benchmark error

outcome: benchmark early abort: Benchmark early abort: 249.757s vs baseline 247.307s (-1.0%, need 5.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.339 | 11.175 |
| 62.004 | 726.577 |
| 4.583 | 48.957 |
| 16.324 | 185.630 |
| 16.328 | 185.930 |
| 23.566 | 276.340 |
| 15.669 | 183.239 |
| 19.665 | 230.596 |
| 12.223 | 141.784 |
| 21.318 | 248.492 |
| 14.333 | 165.836 |
| 6.090 | 68.534 |
| 1.517 | 12.134 |
| 8.362 | 92.152 |
| 15.165 | 173.150 |
| 0.938 | 7.872 |
| 0.735 | 6.057 |
| 1.338 | 10.596 |
| 2.052 | 20.804 |
| 3.844 | 42.142 |
| 2.364 | 23.423 |

# Totals
| user | cpu |
| ---- | ---- |
| 249.757 | 2861.420 |

# Averages
| user | cpu |
| ---- | ---- |
| 11.893 | 136.258 |
