perf: add exact no-mask CPU helper for the fine preset family

Add a dedicated CPU helper for the hot no-mask, zero-sharpness family used by instance 13: first and fourth orders active with equal anisotropy, second and third orders active and isotropic, no luminance mask, edge threshold 0, radius_center 0. This avoids the generic all-orders pixel body, mixed feature plumbing, and repeated per-pixel order dispatch, while keeping the logic readable in a single well-named specialized path. Based on prior wins from exact CPU helpers, this is the most likely place to remove substantial whole-image work without disturbing the established traversal.
outcome: improvement
commit: 80bf08cc73
Reduced instance 13 time from 9.691s to 8.691s (+10.3% improvement), reduced sum(user) from 158.077s to 156.664s (~+0.9% improvement)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.651 | 61.637 |
| 8.314 | 93.230 |
| 7.264 | 80.370 |
| 9.237 | 103.029 |
| 9.308 | 103.125 |
| 9.062 | 103.779 |
| 8.750 | 101.041 |
| 8.975 | 102.492 |
| 0.040 | 0.254 |
| 9.844 | 112.401 |
| 9.602 | 109.649 |
| 9.130 | 104.389 |
| 5.920 | 63.243 |
| 8.691 | 96.002 |
| 8.532 | 94.101 |
| 5.504 | 60.244 |
| 5.513 | 61.406 |
| 6.057 | 65.197 |
| 6.675 | 74.935 |
| 7.747 | 88.229 |
| 6.848 | 76.203 |

# Totals
| user | cpu |
| ---- | ---- |
| 156.664 | 1754.956 |

# Averages
| user | cpu |
| ---- | ---- |
| 7.460 | 83.569 |
