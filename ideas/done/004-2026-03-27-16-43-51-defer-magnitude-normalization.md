perf: defer inverse magnitude scaling to the directional correction calculation

Currently, the squared inverse magnitude (`inv_mag_sq`) is multiplied into both the `cos²θ` and `cosθ·sinθ` angular terms during the gradient/Laplacian setup phase. By deferring this normalization and instead factoring it out of the directional correction equation (`dir_corr = (D_unnorm * axial_diff - cross_unnorm * cross_corners) * inv_mag_sq`), we eliminate one floating-point multiplication per channel. This complements the direct `D` computation by avoiding the storage and repeated scaling of pre-normalized angular tensors.
outcome: target not reached: 173.571s vs baseline 172.940s (-0.4%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.713 | 61.112 |
| 9.069 | 101.140 |
| 8.777 | 95.847 |
| 9.176 | 101.068 |
| 9.255 | 100.594 |
| 8.871 | 100.269 |
| 8.510 | 97.519 |
| 8.725 | 99.163 |
| 9.883 | 110.687 |
| 9.713 | 109.152 |
| 9.427 | 107.276 |
| 9.048 | 101.946 |
| 6.368 | 67.465 |
| 9.340 | 103.700 |
| 9.654 | 105.799 |
| 5.781 | 63.201 |
| 5.724 | 63.691 |
| 6.362 | 67.600 |
| 7.836 | 88.544 |
| 9.068 | 103.743 |
| 7.271 | 79.856 |

# Totals
| user | cpu |
| ---- | ---- |
| 173.571 | 1929.372 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.265 | 91.875 |
