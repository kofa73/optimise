perf: add CPU fast path for no-mask zero-sharpness first-plus-fourth local contrast

Add a dedicated CPU helper for the exact shape of instance 14: `has_mask == false`, `sharpness == 0`, `ABCD[1] == ABCD[2] == 0`, and only 1st/4th orders active. That path can delete the generic four-order plumbing, skip inactive-order setup entirely, and keep only the gradient-driven first-order and laplacian-driven fourth-order math. This matches the “preset-specific helpers only when they cut out large mixed-mode plumbing” learning and targets the weakest-improving benchmark instance directly.

outcome: improvement
commit: 11b31eebbb
Reduced instance 14 time from 9.882s to 9.145s (+7.5% improvement), reduced sum(user) from 163.578s to 163.012s (~+0.3% improvement)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.665 | 61.008 |
| 9.502 | 105.452 |
| 9.018 | 101.282 |
| 9.272 | 102.264 |
| 9.253 | 102.808 |
| 9.133 | 103.886 |
| 8.762 | 100.631 |
| 8.980 | 102.835 |
| 0.040 | 0.244 |
| 9.845 | 110.945 |
| 9.508 | 108.800 |
| 9.137 | 103.142 |
| 6.383 | 68.541 |
| 9.641 | 108.135 |
| 9.145 | 100.698 |
| 5.433 | 59.757 |
| 5.422 | 60.636 |
| 6.425 | 69.218 |
| 7.181 | 81.663 |
| 8.386 | 96.119 |
| 6.881 | 75.660 |

# Totals
| user | cpu |
| ---- | ---- |
| 163.012 | 1823.724 |

# Averages
| user | cpu |
| ---- | ---- |
| 7.762 | 86.844 |
