perf: remove unnecessary zero-initialization of local pixel arrays to eliminate dead stack writes

In `heat_PDE_diffusion`, intermediate local arrays (like `c2`, `cos_theta_grad_sq`, `sin_theta_lapl_sq`, and `variance`) are declared with `= { 0.f }` zero-initializers inside the innermost pixel loop. Because these arrays decay to pointers when passed to `accumulate_convolution_direct` (which carries OpenMP SIMD pragmas), the compiler is often forced to physically allocate them on the stack and emit explicit vector zeroing instructions, wasting significant L1 memory bandwidth per pixel. Since `variance` is unconditionally overwritten, and the angle/`c2` arrays are strictly fully populated prior to any anisotropic use (and completely ignored during isotropic passes), the initial zeroing is mathematically dead code. Removing these initializers eliminates redundant memory stores and removes a strict barrier to variable scalarization without altering the mathematical output.
outcome: benchmark early abort: Benchmark early abort: 222.105s vs baseline 217.223s (-2.2%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.910 | 6.068 |
| 56.782 | 656.077 |
| 4.445 | 47.194 |
| 12.882 | 146.214 |
| 13.266 | 146.177 |
| 21.929 | 252.008 |
| 14.702 | 167.159 |
| 18.327 | 210.010 |
| 12.520 | 144.500 |
| 16.566 | 188.256 |
| 10.948 | 125.791 |
| 5.000 | 51.055 |
| 1.504 | 11.760 |
| 7.327 | 79.906 |
| 14.510 | 161.159 |
| 0.905 | 7.109 |
| 0.732 | 5.555 |
| 1.310 | 9.946 |
| 1.934 | 18.896 |
| 3.461 | 37.334 |
| 2.145 | 20.630 |

# Totals
| user | cpu |
| ---- | ---- |
| 222.105 | 2492.804 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.576 | 118.705 |
