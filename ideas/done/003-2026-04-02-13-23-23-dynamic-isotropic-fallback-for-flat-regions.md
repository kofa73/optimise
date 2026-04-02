perf: dynamically fallback to fast isotropic accumulation in flat regions

In anisotropic diffusion, when the local gradient magnitude (`mag_sq_grad` or `mag_sq_lapl`) is negligible (e.g., in spatially flat surfaces, sky, or completely out-of-focus areas), the conductance tensor math converges to pure isotropic diffusion (`c2` approaches 1.0, yielding `alpha = 1.0`, `beta = 0.0`). By explicitly branching on `mag_sq_grad < FLT_EPSILON` inside the pixel loops to dynamically bypass the expensive `sqrtf`, inverse magnitude scaling, `dt_vector_exp`, and directional correction math, we can fall back to the extremely cheap `accumulate_isotropic` operator for that pixel. This leverages spatial sparsity to delete massive amounts of inner-loop ALU across all anisotropic presets.
outcome: benchmark early abort: Benchmark early abort: 262.043s vs baseline 158.077s (-65.8%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.962 | 61.395 |
| 8.328 | 93.459 |
| 8.752 | 98.529 |
| 21.055 | 238.760 |
| 21.013 | 238.337 |
| 19.253 | 221.238 |
| 18.648 | 215.277 |
| 19.183 | 221.493 |
| 0.040 | 0.248 |
| 20.054 | 230.300 |
| 19.692 | 225.955 |
| 18.737 | 215.508 |
| 7.248 | 79.307 |
| 17.666 | 198.774 |
| 10.200 | 114.550 |
| 5.531 | 61.021 |
| 5.768 | 62.196 |
| 7.430 | 82.306 |
| 6.751 | 76.269 |
| 8.102 | 88.590 |
| 12.630 | 145.477 |

# Totals
| user | cpu |
| ---- | ---- |
| 262.043 | 2968.989 |

# Averages
| user | cpu |
| ---- | ---- |
| 12.478 | 141.380 |
