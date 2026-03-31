perf: specialize heat_PDE_diffusion for fourth-order-only masked inpaint

Add a dedicated CPU wrapper selected when `first == second == third == 0`, `sharpness == 0`, `regularization == 0`, and only `fourth` is active. That variant would compute only the HF laplacian orientation, only the 4th-order anisotropic kernel, and write `LF + HF + update` directly, instead of carrying four `c2` vectors, four kernels, four derivative accumulators, and generic accumulation code. This is a cleaner specialization than inner-loop order skipping because the compiler sees a single fixed algorithm.

outcome: target not reached: 167.218s vs baseline 167.053s (+0.4%, need 3.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.663 | 61.175 |
| 9.518 | 105.444 |
| 9.028 | 101.545 |
| 9.279 | 102.205 |
| 9.224 | 102.623 |
| 9.111 | 103.747 |
| 8.739 | 100.590 |
| 8.911 | 102.432 |
| 0.040 | 0.256 |
| 9.838 | 111.702 |
| 9.532 | 109.410 |
| 9.137 | 103.747 |
| 6.397 | 68.709 |
| 9.660 | 108.580 |
| 9.916 | 109.769 |
| 5.909 | 65.712 |
| 5.924 | 66.756 |
| 6.426 | 69.257 |
| 8.055 | 92.112 |
| 9.406 | 108.473 |
| 7.505 | 83.492 |

# Totals
| user | cpu |
| ---- | ---- |
| 167.218 | 1877.736 |

# Averages
| user | cpu |
| ---- | ---- |
| 7.963 | 89.416 |
