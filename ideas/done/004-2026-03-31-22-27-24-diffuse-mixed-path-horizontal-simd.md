perf: add a peeled horizontal SIMD helper for the active first-plus-fourth CPU path

The proven SIMD work targeted fully isotropic diffusion, but instance 14 spends its time in a mixed path with exactly one LF order and one HF order active. Add a separate peeled interior helper that processes several columns at once for that first-plus-fourth, no-mask configuration while preserving the existing row order and border path. This gives the compiler a much simpler cross-pixel loop than the current generic mixed-order pixel body and avoids paying the control-flow cost of inactive modes.
outcome: target not reached: 162.503s vs baseline 163.578s (+10.6%, need 3.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.652 | 61.357 |
| 9.585 | 106.498 |
| 8.969 | 100.846 |
| 9.295 | 103.294 |
| 9.339 | 103.193 |
| 9.020 | 102.817 |
| 8.671 | 99.154 |
| 8.825 | 101.241 |
| 0.040 | 0.246 |
| 9.880 | 111.130 |
| 9.510 | 108.967 |
| 9.058 | 103.619 |
| 6.424 | 68.300 |
| 9.630 | 108.095 |
| 8.839 | 96.832 |
| 5.422 | 59.757 |
| 5.410 | 60.607 |
| 6.417 | 69.328 |
| 7.262 | 81.779 |
| 8.398 | 96.159 |
| 6.857 | 75.915 |

# Totals
| user | cpu |
| ---- | ---- |
| 162.503 | 1819.134 |

# Averages
| user | cpu |
| ---- | ---- |
| 7.738 | 86.625 |
