perf: conditionally skip spatial accumulations when individual ABCD speeds are zero

For mixed-speed presets (like the "local contrast" family where the 1st/4th orders are active but 2nd/3rd are exactly zero), the PDE solver still unconditionally executes `accumulate_convolution_direct` and `accumulate_isotropic` for the zero-speed orders, performing dozens of MADD operations per pixel only to multiply the result by `ABCD=0` at the end. By wrapping the individual accumulation calls and their corresponding `dt_vector_exp` triggers inside the pixel body with a simple, loop-invariant `if (ctx->ABCD[x] != 0.0f)` check, we elegantly bypass the entire spatial tensor accumulation math for inactive orders without inflating binary size via outer-loop unswitching.
outcome: benchmark early abort: Benchmark early abort: 171.058s vs baseline 163.578s (-4.6%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.915 | 60.876 |
| 9.457 | 106.581 |
| 9.038 | 98.562 |
| 9.326 | 103.713 |
| 9.336 | 103.849 |
| 9.514 | 104.802 |
| 8.785 | 101.516 |
| 9.352 | 103.562 |
| 0.040 | 0.260 |
| 10.470 | 119.611 |
| 10.537 | 117.013 |
| 9.695 | 110.928 |
| 6.412 | 68.937 |
| 10.249 | 111.474 |
| 9.771 | 108.900 |
| 5.764 | 62.755 |
| 5.773 | 63.616 |
| 6.405 | 69.404 |
| 8.210 | 93.821 |
| 9.823 | 109.885 |
| 7.186 | 79.914 |

# Totals
| user | cpu |
| ---- | ---- |
| 171.058 | 1899.979 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.146 | 90.475 |
