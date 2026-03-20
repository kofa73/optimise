perf: extract (1.0f - c2) common subexpression to reduce anisotropic tensor ALUs

In `accumulate_convolution_direct`, the anisotropic tensor weights `a11`, `a22`, and `b11` all fundamentally depend on the difference `(1.0f - c2[c])`. By calculating this as a scalar common subexpression (`inv_c2 = 1.0f - c2[c]`) and rewriting the formulas (e.g., `a11 = c2 + cos2 * inv_c2`), we can compute all three tensor coefficients with only 2 multiplications and 2 additions, down from the current 4 multiplications and 3 additions. This noticeably reduces critical-path ALU pressure in the innermost accumulation loop.
outcome: benchmark early abort: Benchmark early abort: 226.856s vs baseline 217.223s (-4.4%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.912 | 6.062 |
| 57.208 | 660.024 |
| 4.581 | 48.249 |
| 13.198 | 149.467 |
| 13.598 | 148.830 |
| 22.667 | 260.459 |
| 15.294 | 173.117 |
| 18.987 | 217.267 |
| 12.362 | 142.360 |
| 17.134 | 194.596 |
| 11.384 | 130.196 |
| 5.173 | 52.664 |
| 1.514 | 11.963 |
| 7.469 | 81.554 |
| 14.637 | 162.723 |
| 0.941 | 7.395 |
| 0.742 | 5.754 |
| 1.328 | 10.224 |
| 1.975 | 19.359 |
| 3.556 | 38.604 |
| 2.196 | 21.320 |

# Totals
| user | cpu |
| ---- | ---- |
| 226.856 | 2542.187 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.803 | 121.057 |
