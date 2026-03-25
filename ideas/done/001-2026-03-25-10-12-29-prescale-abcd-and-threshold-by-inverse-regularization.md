perf: scale ABCD and threshold by inverse regularization factor to remove inner-loop multiply

The PDE solver currently computes its denominator by multiplying the variance sum of squares by `regularization_factor` for every channel in the inner loop. By mathematically factoring this out—dividing both the `ABCD` speed constants and the `variance_threshold` by `regularization_factor` once per scale outside the spatial loop—we can evaluate the division as `(ABCD_scaled * conv) / (sum_of_squares + threshold_scaled)`. This eliminates the per-channel `variance[c] * regularization_factor` multiplication entirely, replacing it with a lower-latency addition (or zero operations for presets like "sharpen demosaicing" where the threshold is exactly zero).
outcome: target not reached: 173.398s vs baseline 172.940s (-0.3%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.612 | 60.690 |
| 9.315 | 103.664 |
| 8.568 | 96.471 |
| 9.171 | 102.473 |
| 9.228 | 102.437 |
| 8.873 | 101.668 |
| 8.568 | 98.910 |
| 8.713 | 100.481 |
| 9.748 | 110.076 |
| 9.791 | 111.591 |
| 9.518 | 109.481 |
| 9.131 | 104.199 |
| 6.326 | 68.422 |
| 9.323 | 104.073 |
| 9.530 | 106.792 |
| 5.720 | 63.970 |
| 5.778 | 65.252 |
| 6.333 | 68.660 |
| 7.741 | 88.704 |
| 9.093 | 104.173 |
| 7.318 | 82.020 |

# Totals
| user | cpu |
| ---- | ---- |
| 173.398 | 1954.207 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.257 | 93.057 |
