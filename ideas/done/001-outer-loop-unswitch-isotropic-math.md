Skip gradient/laplacian angle math for isotropic orders via outer-loop unswitching

For isotropic diffusion, the convolution kernel purely relies on central and neighbor pixel sums, completely ignoring the gradient/laplacian magnitudes, trigonometric angles, and `c2` weights. However, the expensive calculations for these unused values (`sqrtf` for magnitude, divisions for `cos_grad`/`sin_grad`, and multiple squares) are still executed unconditionally. Since inner-loop branching disrupts SIMD vectorization (as learned from past regressions), we can manually unswitch the row loop at the outer level based on whether the gradient orders (0 and 2) or laplacian orders (1 and 3) are strictly isotropic. Many popular, heavy presets (e.g., 'lens deblur', 'dehaze') use zero anisotropy for the laplacian orders. Evaluating this outside the innermost loop safely skips ~50% of the heavy per-pixel math (saving dozens of operations, square roots, and divisions per pixel) without introducing any SIMD-breaking branches or altering floating-point evaluation order.

outcome: improvement
commit: 36ef9f0625
Reduced sum(user) from 231.975s to 217.223s (~6.4% improvement)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.863 | 6.034 |
| 56.006 | 658.119 |
| 4.368 | 46.526 |
| 12.718 | 143.887 |
| 12.757 | 144.771 |
| 21.470 | 250.866 |
| 14.296 | 166.529 |
| 17.860 | 208.938 |
| 12.221 | 140.872 |
| 16.152 | 187.824 |
| 10.842 | 124.680 |
| 4.637 | 51.302 |
| 1.457 | 11.478 |
| 7.220 | 78.843 |
| 14.225 | 161.619 |
| 0.851 | 6.676 |
| 0.679 | 5.240 |
| 1.273 | 9.962 |
| 1.847 | 18.374 |
| 3.386 | 36.873 |
| 2.095 | 20.416 |

# Totals
| user | cpu |
| ---- | ---- |
| 217.223 | 2479.829 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.344 | 118.087 |
