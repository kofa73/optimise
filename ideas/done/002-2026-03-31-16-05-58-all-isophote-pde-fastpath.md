perf: add a no-mask all-isophote CPU fast path for diffuse PDE

Add a dedicated CPU helper for the case where `has_mask == false` and all four orders use `DT_ISOTROPY_ISOPHOTE`, which matches the targeted strong parameters (`anisotropy_* = 1.0`). That path can bypass the generic mixed-mode plumbing in `heat_PDE_diffusion()`, drop unused isotropic/gradient branches, and keep only the math relevant to the benchmarked preset, while preserving the existing generic helper for other parameter combinations.
outcome: improvement
commit: c09b0cbacd
Reduced sum(user) from 167.053s to 163.578s (~10.8% improvement)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.658 | 61.131 |
| 9.407 | 105.933 |
| 9.117 | 101.087 |
| 9.236 | 102.858 |
| 9.281 | 102.007 |
| 9.058 | 103.552 |
| 8.704 | 100.704 |
| 8.980 | 102.265 |
| 0.039 | 0.246 |
| 9.718 | 111.064 |
| 9.581 | 109.018 |
| 9.068 | 103.775 |
| 6.385 | 68.678 |
| 9.716 | 107.995 |
| 9.882 | 110.559 |
| 5.424 | 59.477 |
| 5.409 | 60.609 |
| 6.418 | 69.332 |
| 7.234 | 81.592 |
| 8.420 | 95.812 |
| 6.843 | 76.062 |

# Totals
| user | cpu |
| ---- | ---- |
| 163.578 | 1833.756 |

# Averages
| user | cpu |
| ---- | ---- |
| 7.789 | 87.322 |
