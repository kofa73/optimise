perf: absorb variance regularization factor into ABCD constants when threshold is zero

The per-pixel variance is calculated as `variance = threshold + sum_sq * reg_factor`, followed by the division `acc / variance`. For presets like "sharpen demosaicing" where `variance_threshold` is exactly `0.0f`, this mathematically becomes `acc / (sum_sq * reg_factor)`. Since `acc` is a linear combination of the `ABCD` speeds, we can factor `reg_factor` out of the denominator and mathematically absorb `1.0f / reg_factor` directly into the loop-invariant `ABCD` constants before the row loop. This allows the inner loop to divide directly by the unscaled `sum_sq`, eliminating an expensive inner-loop FMA multiplication per channel without requiring loop unswitching.
outcome: target not reached: 174.869s vs baseline 175.941s (+0.6%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.631 | 60.616 |
| 9.536 | 106.106 |
| 8.715 | 98.146 |
| 9.260 | 103.377 |
| 9.358 | 103.470 |
| 8.924 | 102.231 |
| 8.622 | 99.254 |
| 8.757 | 100.942 |
| 9.757 | 110.197 |
| 9.745 | 110.506 |
| 9.456 | 108.639 |
| 9.070 | 103.527 |
| 6.294 | 67.742 |
| 9.481 | 105.977 |
| 9.673 | 107.589 |
| 5.924 | 66.384 |
| 5.975 | 67.354 |
| 6.333 | 68.021 |
| 7.734 | 88.469 |
| 9.076 | 103.636 |
| 7.548 | 84.700 |

# Totals
| user | cpu |
| ---- | ---- |
| 174.869 | 1966.883 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.327 | 93.661 |
