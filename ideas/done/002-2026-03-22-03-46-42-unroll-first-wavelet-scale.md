perf: Unroll first wavelet scale to statically constant-fold diffusion step size

Because `heat_PDE_diffusion` is called inside a dynamic loop over `scales`, the spatial step size `mult` is a runtime variable. This forces the compiler to generate dynamic pointer arithmetic for the 9-point stencil memory fetches (e.g., calculating `j - col_step` at runtime). By explicitly peeling the `s == 0` (where `mult = 1`) iteration outside the scale loop, we allow the compiler to instantiate a fully static version of the PDE solver for the finest detail layer. This turns all dynamic memory offsets into exact compile-time constants (e.g., exactly `-4` or `+4` bytes for lateral neighbors), drastically improving auto-vectorization and memory access speed for the most computationally intensive scale.
outcome: target not reached: 207.661s vs baseline 206.974s (-0.3%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.900 | 6.045 |
| 51.595 | 594.392 |
| 4.132 | 42.837 |
| 12.517 | 137.793 |
| 12.511 | 138.551 |
| 20.827 | 237.310 |
| 13.686 | 157.270 |
| 17.145 | 196.720 |
| 12.371 | 138.873 |
| 15.414 | 177.157 |
| 10.394 | 117.551 |
| 4.449 | 47.517 |
| 1.449 | 10.749 |
| 6.965 | 73.684 |
| 13.423 | 150.387 |
| 0.868 | 6.107 |
| 0.689 | 4.940 |
| 1.292 | 9.386 |
| 1.798 | 16.902 |
| 3.221 | 33.887 |
| 2.015 | 18.854 |

# Totals
| user | cpu |
| ---- | ---- |
| 207.661 | 2316.912 |

# Averages
| user | cpu |
| ---- | ---- |
| 9.889 | 110.329 |
