perf: Skip gradient/laplacian angle math for isotropic orders via outer-loop unswitching

For isotropic diffusion, the convolution kernel purely relies on central and neighbor pixel sums, completely ignoring the gradient/laplacian magnitudes, trigonometric angles, and `c2` weights. However, the expensive calculations for these unused values (`sqrtf` for magnitude, divisions for `cos_grad`/`sin_grad`, and multiple squares) are still executed unconditionally. Since inner-loop branching disrupts SIMD vectorization (as learned from past regressions), we can manually unswitch the row loop at the outer level based on whether the gradient orders (0 and 2) or laplacian orders (1 and 3) are strictly isotropic. Many popular, heavy presets (e.g., 'lens deblur', 'dehaze') use zero anisotropy for the laplacian orders. Evaluating this outside the innermost loop safely skips ~50% of the heavy per-pixel math (saving dozens of operations, square roots, and divisions per pixel) without introducing any SIMD-breaking branches or altering floating-point evaluation order.
outcome: benchmark early abort: Benchmark early abort: 237.543s vs baseline 247.307s (+3.9%, need 5.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.157 | 9.539 |
| 55.202 | 651.773 |
| 4.579 | 48.752 |
| 14.549 | 166.583 |
| 14.546 | 165.395 |
| 25.421 | 298.633 |
| 16.920 | 198.243 |
| 21.263 | 249.744 |
| 12.237 | 141.835 |
| 19.135 | 223.877 |
| 12.845 | 148.838 |
| 5.467 | 61.322 |
| 1.678 | 14.229 |
| 7.444 | 81.904 |
| 14.614 | 167.364 |
| 0.884 | 6.950 |
| 0.692 | 5.399 |
| 1.475 | 12.232 |
| 1.865 | 18.555 |
| 3.448 | 37.650 |
| 2.122 | 20.732 |

# Totals
| user | cpu |
| ---- | ---- |
| 237.543 | 2729.549 |

# Averages
| user | cpu |
| ---- | ---- |
| 11.312 | 129.979 |
