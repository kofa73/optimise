perf: add CPU fast path for no-mask zero-sharpness first-plus-fourth local contrast

Add a dedicated CPU helper for the exact shape of instance 14: `has_mask == false`, `sharpness == 0`, `ABCD[1] == ABCD[2] == 0`, and only 1st/4th orders active. That path can delete the generic four-order plumbing, skip inactive-order setup entirely, and keep only the gradient-driven first-order and laplacian-driven fourth-order math. This matches the “preset-specific helpers only when they cut out large mixed-mode plumbing” learning and targets the weakest-improving benchmark instance directly.
outcome: target not reached: 163.176s vs baseline 163.578s (+7.5%, need 3.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.665 | 61.163 |
| 9.515 | 106.965 |
| 9.022 | 101.471 |
| 9.312 | 102.061 |
| 9.263 | 102.927 |
| 9.145 | 103.969 |
| 8.750 | 100.780 |
| 8.925 | 102.498 |
| 0.040 | 0.249 |
| 9.833 | 111.878 |
| 9.483 | 108.653 |
| 9.145 | 103.180 |
| 6.401 | 68.591 |
| 9.710 | 108.803 |
| 9.140 | 100.397 |
| 5.451 | 59.903 |
| 5.427 | 60.651 |
| 6.422 | 69.358 |
| 7.223 | 81.782 |
| 8.422 | 96.260 |
| 6.882 | 75.776 |

# Totals
| user | cpu |
| ---- | ---- |
| 163.176 | 1827.315 |

# Averages
| user | cpu |
| ---- | ---- |
| 7.770 | 87.015 |
