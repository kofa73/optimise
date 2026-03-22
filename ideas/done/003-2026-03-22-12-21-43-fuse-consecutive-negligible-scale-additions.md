perf: combine consecutive negligible-scale reconstructions into a single fused addition pass

When multiple consecutive wavelet scales have negligible Gaussian norm weight, the current code performs separate full-buffer passes for each: out1 = HF[s] + LF_s, then out2 = HF[s-1] + out1, etc. Each pass reads and writes the entire image buffer. By pre-scanning which scales are negligible and grouping consecutive negligible scales, we can fuse their HF additions into a single pass: output = HF[s] + HF[s-1] + ... + HF[s-k] + LF_s, performing one read from each HF buffer and one write, eliminating k-1 intermediate read+write passes. For presets with large radius_center (where many inner scales are negligible), this can save significant memory bandwidth. This follows the proven pattern of function-level guards and algebraic absorption.
outcome: target not reached: 191.291s vs baseline 190.343s (-0.5%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.868 | 5.417 |
| 51.123 | 592.950 |
| 4.124 | 43.117 |
| 12.012 | 134.346 |
| 11.997 | 135.264 |
| 17.350 | 196.972 |
| 10.242 | 118.143 |
| 13.641 | 157.447 |
| 10.901 | 122.264 |
| 15.328 | 176.848 |
| 8.655 | 97.432 |
| 4.435 | 47.681 |
| 1.421 | 10.610 |
| 5.987 | 64.432 |
| 13.342 | 148.680 |
| 0.832 | 6.101 |
| 0.699 | 5.071 |
| 1.253 | 9.096 |
| 1.812 | 17.459 |
| 3.242 | 34.612 |
| 2.027 | 18.979 |

# Totals
| user | cpu |
| ---- | ---- |
| 191.291 | 2142.921 |

# Averages
| user | cpu |
| ---- | ---- |
| 9.109 | 102.044 |
