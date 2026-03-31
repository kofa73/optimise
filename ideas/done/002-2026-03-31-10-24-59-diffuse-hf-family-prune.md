perf: prune the unused LF-gradient derivative family on HF-only masked scales

Add a small active-family descriptor in `wavelets_process` that tells `heat_PDE_diffusion` whether the LF-gradient side, the HF-laplacian side, or both are needed. For the benchmark preset only the fourth-order HF path matters, so the LF gradient fetch/normalize path, its unused `dt_vector_exp` calls, and its unused kernel/derivative accumulations can be skipped entirely. This is a focused reduction of expensive setup work, not a broad rewrite of the pixel body.
outcome: benchmark early abort: Benchmark early abort: 323.504s vs baseline 167.053s (-93.7%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 9.250 | 104.361 |
| 18.406 | 208.926 |
| 15.237 | 171.889 |
| 19.303 | 220.632 |
| 19.546 | 220.916 |
| 17.580 | 201.355 |
| 17.031 | 196.124 |
| 17.474 | 200.784 |
| 0.040 | 0.255 |
| 19.302 | 221.461 |
| 18.604 | 217.325 |
| 18.045 | 206.470 |
| 10.757 | 117.113 |
| 20.581 | 234.125 |
| 20.595 | 233.100 |
| 11.174 | 128.693 |
| 11.603 | 130.889 |
| 10.592 | 119.708 |
| 15.751 | 180.366 |
| 18.423 | 211.964 |
| 14.210 | 164.110 |

# Totals
| user | cpu |
| ---- | ---- |
| 323.504 | 3690.566 |

# Averages
| user | cpu |
| ---- | ---- |
| 15.405 | 175.741 |
