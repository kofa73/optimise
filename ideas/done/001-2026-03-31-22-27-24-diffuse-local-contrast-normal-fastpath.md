perf: add no-mask local-contrast-normal CPU PDE fast path

For instance 14 the hot path is fixed: `has_mask == FALSE`, `sharpness == 0`, only 1st and 4th orders are active, and both use the same negative anisotropy. Add a dedicated helper for that shape so `heat_PDE_diffusion()` computes only one LF gradient tensor and one HF laplacian tensor, builds only the two needed kernels, skips the generic 4-order arrays/loops, and folds the `strength == 1` reconstruction directly into the output. This matches the one preset-specific helper pattern that has already paid off, but targets the currently underperforming local-contrast preset instead of the all-isophote case.
outcome: target not reached: 162.688s vs baseline 163.578s (+12.8%, need 3.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.677 | 61.361 |
| 9.477 | 105.612 |
| 9.029 | 101.477 |
| 9.235 | 102.799 |
| 9.313 | 102.386 |
| 9.139 | 104.174 |
| 8.785 | 101.180 |
| 8.951 | 102.779 |
| 0.040 | 0.251 |
| 9.876 | 111.737 |
| 9.623 | 109.322 |
| 9.075 | 103.637 |
| 6.428 | 68.287 |
| 9.640 | 108.148 |
| 8.615 | 94.314 |
| 5.427 | 59.690 |
| 5.429 | 60.716 |
| 6.387 | 69.067 |
| 7.266 | 81.369 |
| 8.410 | 96.424 |
| 6.866 | 76.101 |

# Totals
| user | cpu |
| ---- | ---- |
| 162.688 | 1820.831 |

# Averages
| user | cpu |
| ---- | ---- |
| 7.747 | 86.706 |
