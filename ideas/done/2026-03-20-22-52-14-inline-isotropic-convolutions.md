perf: Directly inline isotropic convolutions to bypass function overhead

When the macro flags `GRAD_ISOTROPIC` or `LAPL_ISOTROPIC` are true, the pixel solver currently still initializes zeroed dummy arrays and calls the generalized `accumulate_convolution_direct` function, which internally hits a runtime switch statement. By directly inlining the simple isotropic accumulation math into a compile-time `if (GRAD_ISOTROPIC)` branch inside the macro, we completely eliminate the function call boundary, dummy array instantiation, and switch branching for isotropic passes.
outcome: target not reached: 205.876s vs baseline 206.974s (+0.5%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.904 | 5.930 |
| 51.406 | 588.397 |
| 4.137 | 42.685 |
| 12.284 | 137.285 |
| 12.364 | 136.331 |
| 20.408 | 234.510 |
| 13.420 | 155.213 |
| 16.930 | 194.526 |
| 12.383 | 138.381 |
| 15.213 | 175.125 |
| 10.276 | 115.717 |
| 4.395 | 46.877 |
| 1.448 | 10.567 |
| 6.967 | 74.334 |
| 13.484 | 151.197 |
| 0.867 | 6.025 |
| 0.694 | 5.004 |
| 1.272 | 9.307 |
| 1.797 | 16.195 |
| 3.212 | 33.135 |
| 2.015 | 18.689 |

# Totals
| user | cpu |
| ---- | ---- |
| 205.876 | 2295.430 |

# Averages
| user | cpu |
| ---- | ---- |
| 9.804 | 109.306 |
