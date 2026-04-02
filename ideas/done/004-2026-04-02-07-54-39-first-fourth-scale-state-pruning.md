perf: prune second-and-third-order scale state from the first-plus-fourth pipeline

For presets like instance 14 where only 1st and 4th orders are enabled, build a smaller per-scale runtime that does not allocate, initialize, or traverse any metadata, coefficient arrays, or helper state used exclusively by 2nd/3rd-order diffusion. This is broader than skipping zero-speed math inside the pixel loop: it deletes control-plane and full-pass setup work across the wavelet/PDE pipeline, while keeping the readable structure of the active orders intact.
outcome: target not reached: instance 18 regressed from 7.225s to 7.232s (-0.1%, need 3.0%), overall sum(user) improved from 160.993s to 160.568s (+0.3%); failed gate: target threshold

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.698 | 61.567 |
| 9.503 | 106.324 |
| 7.255 | 80.609 |
| 9.280 | 103.514 |
| 9.294 | 102.356 |
| 9.062 | 103.579 |
| 8.780 | 101.060 |
| 8.897 | 102.579 |
| 0.039 | 0.261 |
| 9.857 | 111.619 |
| 9.515 | 109.210 |
| 9.091 | 104.273 |
| 6.441 | 69.159 |
| 9.648 | 108.594 |
| 8.541 | 94.402 |
| 5.407 | 59.809 |
| 5.393 | 60.769 |
| 6.411 | 69.791 |
| 7.232 | 81.908 |
| 8.394 | 96.619 |
| 6.830 | 76.151 |

# Totals
| user | cpu |
| ---- | ---- |
| 160.568 | 1804.153 |

# Averages
| user | cpu |
| ---- | ---- |
| 7.646 | 85.912 |
