perf: add a no-mask third-plus-fourth-order watercolor CPU helper

Add a dedicated CPU path for the benchmarked watercolor shape: no mask, zero sharpness, zero first/second-order speed, and only anisotropic third/fourth-order diffusion active. This should remove the generic four-order plumbing, dead low-order state, and mixed-mode branches from the hottest PDE loop while keeping the spatial traversal unchanged. It follows the pattern of prior preset-specific wins, but targets the under-improved instance directly instead of the existing local-contrast or all-isophote helpers.
outcome: improvement
commit: beba5fadba
Reduced instance 2 time from 9.018s to 7.300s (+19.1% improvement), reduced sum(user) from 163.012s to 161.306s (~+1.0% improvement)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.695 | 61.494 |
| 9.395 | 106.353 |
| 7.300 | 80.391 |
| 9.247 | 103.320 |
| 9.237 | 103.125 |
| 9.132 | 104.331 |
| 8.743 | 101.083 |
| 8.998 | 103.097 |
| 0.040 | 0.255 |
| 9.760 | 111.842 |
| 9.606 | 109.404 |
| 9.085 | 104.195 |
| 6.402 | 69.180 |
| 9.749 | 108.470 |
| 9.154 | 101.540 |
| 5.386 | 59.945 |
| 5.463 | 60.666 |
| 6.404 | 69.539 |
| 7.184 | 82.167 |
| 8.467 | 96.067 |
| 6.859 | 76.410 |

# Totals
| user | cpu |
| ---- | ---- |
| 161.306 | 1812.874 |

# Averages
| user | cpu |
| ---- | ---- |
| 7.681 | 86.327 |
