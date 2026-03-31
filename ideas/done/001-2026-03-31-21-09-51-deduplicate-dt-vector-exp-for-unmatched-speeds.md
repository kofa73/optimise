perf: deduplicate dt_vector_exp evaluations when anisotropies match but speeds differ

The current `GRAD_MATCHED` and `LAPL_MATCHED` fast paths successfully deduplicate `dt_vector_exp` calls, but strictly require both the anisotropy *and* the ABCD speeds to match. For presets like "sharpness | strong" where speeds differ (e.g., `first = 0.0065`, `third = -0.25`) but anisotropies are identical (`anisotropy = 1.0`), the matched flag is false. Consequently, the pixel body completely re-evaluates the expensive `dt_vector_exp` for the secondary order using the exact same `c2` input values. By adding a loop-invariant condition `if (ctx->half_anisotropy[0] == ctx->half_anisotropy[2])` to simply copy the evaluated `c2[0]` into `c2[2]` (and similarly for Laplacian orders), we can cleanly bypass up to 8 redundant `expf` calls per pixel regardless of speed differences.
outcome: benchmark early abort: Benchmark early abort: 173.830s vs baseline 163.578s (-6.3%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.668 | 61.537 |
| 9.431 | 106.017 |
| 10.401 | 113.941 |
| 9.253 | 102.688 |
| 9.518 | 102.179 |
| 9.116 | 104.089 |
| 9.092 | 100.941 |
| 8.945 | 102.581 |
| 0.040 | 0.263 |
| 10.399 | 118.772 |
| 10.495 | 116.487 |
| 9.680 | 111.109 |
| 7.104 | 73.091 |
| 10.770 | 121.555 |
| 11.207 | 122.016 |
| 5.554 | 61.495 |
| 5.543 | 62.051 |
| 7.057 | 75.319 |
| 7.941 | 89.738 |
| 9.285 | 106.181 |
| 7.331 | 77.951 |

# Totals
| user | cpu |
| ---- | ---- |
| 173.830 | 1930.001 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.278 | 91.905 |
