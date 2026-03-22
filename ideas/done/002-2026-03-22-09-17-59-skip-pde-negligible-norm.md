perf: skip PDE solver for wavelet scales where Gaussian norm weight is negligible

Before calling heat_PDE_diffusion for each wavelet scale, check whether the Gaussian norm weight makes the correction negligible (e.g. all |ABCD[k]| < FLT_EPSILON and |strength - 1.0f| < FLT_EPSILON). For scales far from the user's center radius, the norm decays exponentially toward zero (e.g. for radius=8, norm drops below 0.0002 by scale 4). When the correction is negligible, replace the full per-pixel PDE solver with a simple parallel memcpy-add of `output = HF[s] + buffer_in`, using nontemporal stores. This is a function-call-level check (not a per-pixel branch), so it carries none of the SIMD-breaking penalty that caused per-pixel skip attempts to regress. For presets with many scales but narrow center radius (like "lens deblur" with radius=8-12 and 4-5 scales), this can eliminate entire PDE passes for the outermost scales.
outcome: improvement
commit: d2c7b0d689
Reduced sum(user) from 204.349s to 200.347s (~2.0% improvement)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.842 | 5.291 |
| 51.080 | 593.940 |
| 4.091 | 42.348 |
| 11.965 | 133.982 |
| 11.977 | 134.556 |
| 19.957 | 228.012 |
| 12.895 | 148.167 |
| 16.233 | 187.859 |
| 10.896 | 122.175 |
| 15.312 | 176.564 |
| 9.964 | 112.451 |
| 4.408 | 47.597 |
| 1.406 | 10.491 |
| 6.375 | 67.850 |
| 13.084 | 147.503 |
| 0.863 | 6.310 |
| 0.713 | 4.898 |
| 1.254 | 9.130 |
| 1.802 | 16.722 |
| 3.216 | 33.878 |
| 2.014 | 18.874 |

# Totals
| user | cpu |
| ---- | ---- |
| 200.347 | 2248.598 |

# Averages
| user | cpu |
| ---- | ---- |
| 9.540 | 107.076 |
