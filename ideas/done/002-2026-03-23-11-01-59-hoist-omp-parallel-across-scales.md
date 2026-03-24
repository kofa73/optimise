perf: wrap multi-scale decomposition and reconstruction in single OMP parallel regions

Currently each scale's decomposition (`decompose_2D_Bspline_diffuse`) and each scale's PDE solver (`heat_PDE_diffusion`) launch separate OpenMP parallel regions via `DT_OMP_FOR()`. For 8 scales × 8 iterations, this means 128+ parallel region launches per `process()` call. Hoist the `#pragma omp parallel` to encompass the entire `for(s=0; s<scales; ++s)` decomposition loop and the entire `for(s=scales-1; s>=0; --s)` reconstruction loop, using `#pragma omp for` (with implicit barriers) inside each scale iteration. This eliminates per-scale thread pool wake-up overhead while the per-thread temp buffer allocation (`dt_alloc_perthread_float`) can be shared across scales. Expected gain is 1-5%, more pronounced for smaller images where threading overhead is proportionally larger.
outcome: benchmark early abort: Benchmark early abort: 186.356s vs baseline 181.409s (-2.7%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.652 | 61.829 |
| 10.627 | 116.990 |
| 8.846 | 99.783 |
| 10.684 | 116.216 |
| 10.412 | 117.459 |
| 9.663 | 106.706 |
| 9.124 | 105.316 |
| 9.205 | 106.434 |
| 9.963 | 109.459 |
| 10.635 | 122.301 |
| 10.687 | 119.254 |
| 9.937 | 114.530 |
| 6.484 | 65.988 |
| 9.546 | 107.365 |
| 9.735 | 109.195 |
| 6.774 | 72.299 |
| 6.545 | 74.258 |
| 6.187 | 67.370 |
| 8.179 | 89.843 |
| 9.178 | 106.149 |
| 8.293 | 93.437 |

# Totals
| user | cpu |
| ---- | ---- |
| 186.356 | 2082.181 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.874 | 99.151 |
