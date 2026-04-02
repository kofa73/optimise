perf: peel vertical B-spline border loops to remove hot-pass y clamping

Extend the successful horizontal B-spline peeling idea to the vertical blur/decomposition/reconstruction passes. Split top border, interior rows, and bottom border so the dominant interior loop can use fixed row offsets with no per-pixel `MIN`/`MAX` or clamp arithmetic. The B-spline stages touch the whole image at every scale, so deleting branchy boundary math from their hot interior should give a meaningful win without changing traversal order or algorithm structure.
outcome: target not reached: instance 18 improved from 7.225s to 7.200s (+0.3%, need 3.0%), overall sum(user) regressed from 160.993s to 161.017s (-0.0%); failed gate: target threshold

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.699 | 61.769 |
| 9.420 | 106.377 |
| 7.293 | 80.113 |
| 9.279 | 103.465 |
| 9.265 | 103.345 |
| 9.149 | 104.474 |
| 8.729 | 101.161 |
| 9.006 | 103.014 |
| 0.039 | 0.260 |
| 9.797 | 112.024 |
| 9.642 | 109.580 |
| 9.140 | 104.761 |
| 6.429 | 69.339 |
| 9.735 | 108.602 |
| 8.597 | 94.351 |
| 5.427 | 60.052 |
| 5.449 | 60.931 |
| 6.413 | 69.868 |
| 7.200 | 82.231 |
| 8.438 | 96.263 |
| 6.871 | 76.560 |

# Totals
| user | cpu |
| ---- | ---- |
| 161.017 | 1808.540 |

# Averages
| user | cpu |
| ---- | ---- |
| 7.667 | 86.121 |
