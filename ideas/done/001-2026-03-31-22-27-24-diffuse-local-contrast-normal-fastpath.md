perf: add no-mask local-contrast-normal CPU PDE fast path

For instance 14 the hot path is fixed: `has_mask == FALSE`, `sharpness == 0`, only 1st and 4th orders are active, and both use the same negative anisotropy. Add a dedicated helper for that shape so `heat_PDE_diffusion()` computes only one LF gradient tensor and one HF laplacian tensor, builds only the two needed kernels, skips the generic 4-order arrays/loops, and folds the `strength == 1` reconstruction directly into the output. This matches the one preset-specific helper pattern that has already paid off, but targets the currently underperforming local-contrast preset instead of the all-isophote case.

outcome: target not reached: instance 2 regressed from 9.018s to 9.087s (-0.8%, need 3.0%), overall sum(user) improved from 163.012s to 162.521s (+0.3%); failed gate: target threshold

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.665 | 60.846 |
| 9.370 | 105.528 |
| 9.087 | 100.843 |
| 9.235 | 102.471 |
| 9.302 | 102.390 |
| 9.101 | 103.716 |
| 8.705 | 100.420 |
| 8.965 | 102.239 |
| 0.039 | 0.254 |
| 9.803 | 111.643 |
| 9.632 | 109.073 |
| 9.111 | 104.021 |
| 6.415 | 68.772 |
| 9.701 | 107.583 |
| 8.560 | 94.183 |
| 5.452 | 59.751 |
| 5.432 | 60.639 |
| 6.393 | 69.024 |
| 7.243 | 82.168 |
| 8.450 | 96.061 |
| 6.860 | 76.111 |

# Totals
| user | cpu |
| ---- | ---- |
| 162.521 | 1817.736 |

# Averages
| user | cpu |
| ---- | ---- |
| 7.739 | 86.559 |
