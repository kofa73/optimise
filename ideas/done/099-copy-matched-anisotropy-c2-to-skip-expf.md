perf: Skip redundant dt_vector_exp calculations for matched LF/HF anisotropy

The 1st and 3rd diffusion orders both scale their anisotropy by the LF gradient magnitude, while the 2nd and 4th orders scale by the HF laplacian magnitude. In most standard presets (e.g., deblur, dehaze, denoise), the user's 1st/3rd and 2nd/4th anisotropy parameters are identical. We can calculate loop-invariant booleans (`match_02` and `match_13`) outside the per-pixel loop to detect this symmetry. Inside the loop, if these match, we skip the initialization and expensive `dt_vector_exp` calls for `c2[2]` and `c2[3]`, and instead directly copy the bit-identical, already-computed vectors from `c2[0]` and `c2[1]`. This eliminates up to 8 redundant `expf` evaluations per pixel without altering floating-point bit-exactness.

outcome: benchmark early abort: Benchmark early abort: 399.122s vs baseline 217.223s (-83.7%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.946 | 6.172 |
| 102.768 | 1187.221 |
| 8.278 | 91.964 |
| 25.670 | 291.022 |
| 25.683 | 291.838 |
| 39.733 | 457.563 |
| 26.644 | 306.596 |
| 33.220 | 381.864 |
| 12.672 | 142.160 |
| 29.478 | 341.084 |
| 19.982 | 227.535 |
| 8.354 | 94.587 |
| 2.777 | 26.760 |
| 15.114 | 167.632 |
| 29.563 | 337.223 |
| 1.466 | 13.473 |
| 1.132 | 10.299 |
| 2.653 | 22.148 |
| 3.208 | 34.025 |
| 6.108 | 68.309 |
| 3.673 | 38.534 |

# Totals
| user | cpu |
| ---- | ---- |
| 399.122 | 4538.009 |

# Averages
| user | cpu |
| ---- | ---- |
| 19.006 | 216.096 |
