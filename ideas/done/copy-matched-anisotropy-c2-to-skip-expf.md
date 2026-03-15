perf: Skip redundant dt_vector_exp calculations for matched LF/HF anisotropy

The 1st and 3rd diffusion orders both scale their anisotropy by the LF gradient magnitude, while the 2nd and 4th orders scale by the HF laplacian magnitude. In most standard presets (e.g., deblur, dehaze, denoise), the user's 1st/3rd and 2nd/4th anisotropy parameters are identical. We can calculate loop-invariant booleans (`match_02` and `match_13`) outside the per-pixel loop to detect this symmetry. Inside the loop, if these match, we skip the initialization and expensive `dt_vector_exp` calls for `c2[2]` and `c2[3]`, and instead directly copy the bit-identical, already-computed vectors from `c2[0]` and `c2[1]`. This eliminates up to 8 redundant `expf` evaluations per pixel without altering floating-point bit-exactness.
outcome: benchmark early abort: Benchmark early abort: 250.103s vs baseline 247.307s (-1.1%, need 5.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.242 | 9.666 |
| 58.509 | 683.674 |
| 4.856 | 51.386 |
| 15.457 | 175.159 |
| 15.534 | 175.118 |
| 26.468 | 308.277 |
| 17.674 | 204.441 |
| 22.078 | 256.252 |
| 12.513 | 138.219 |
| 19.937 | 231.061 |
| 13.354 | 153.694 |
| 5.712 | 63.137 |
| 1.748 | 14.819 |
| 8.104 | 88.172 |
| 15.875 | 179.370 |
| 0.926 | 7.465 |
| 0.738 | 5.705 |
| 1.567 | 13.034 |
| 1.972 | 19.608 |
| 3.622 | 39.289 |
| 2.217 | 21.820 |

# Totals
| user | cpu |
| ---- | ---- |
| 250.103 | 2839.366 |

# Averages
| user | cpu |
| ---- | ---- |
| 11.910 | 135.208 |
