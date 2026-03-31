perf: conditionally evaluate secondary tensor magnitudes for matched orders

For order groups where `GRAD_MATCHED` or `LAPL_MATCHED` is true (like the target "sharpen demosaicing / AA filter" preset), the secondary orders (`c2[2]` and `c2[3]`) are never passed to the accumulation function. While the expensive `dt_vector_exp` calls are already correctly unswitched for these matched cases, the initial `magnitude * half_anisotropy` multiplications and array writes for `c2[2]` and `c2[3]` are still unconditionally executed. Wrapping these assignments in `!(GRAD_MATCHED)` and `!(LAPL_MATCHED)` macro conditions allows the compiler to completely dead-code these redundant tensor evaluations.

outcome: target not reached: 166.679s vs baseline 167.053s (+0.6%, need 3.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.642 | 61.258 |
| 9.405 | 104.202 |
| 8.994 | 101.204 |
| 9.195 | 102.378 |
| 9.272 | 102.784 |
| 9.057 | 103.515 |
| 8.712 | 100.284 |
| 8.888 | 102.238 |
| 0.040 | 0.251 |
| 9.846 | 111.728 |
| 9.626 | 109.470 |
| 9.086 | 104.040 |
| 6.403 | 68.424 |
| 9.642 | 108.255 |
| 9.945 | 110.078 |
| 5.840 | 64.661 |
| 5.813 | 65.545 |
| 6.386 | 69.137 |
| 8.082 | 91.785 |
| 9.383 | 108.269 |
| 7.422 | 82.395 |

# Totals
| user | cpu |
| ---- | ---- |
| 166.679 | 1871.901 |

# Averages
| user | cpu |
| ---- | ---- |
| 7.937 | 89.138 |
