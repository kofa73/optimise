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

outcome: target not reached: instance 2 regressed from 9.018s to 9.029s (-0.1%, need 3.0%), overall sum(user) regressed from 163.012s to 163.138s (-0.1%); failed gate: target threshold

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.676 | 61.054 |
| 9.496 | 105.362 |
| 9.029 | 101.602 |
| 9.241 | 102.832 |
| 9.295 | 101.890 |
| 9.100 | 103.879 |
| 8.763 | 100.666 |
| 8.933 | 102.661 |
| 0.039 | 0.257 |
| 9.839 | 110.987 |
| 9.544 | 108.859 |
| 9.070 | 103.701 |
| 6.447 | 68.168 |
| 9.642 | 108.238 |
| 9.265 | 102.079 |
| 5.411 | 59.629 |
| 5.426 | 60.729 |
| 6.410 | 69.520 |
| 7.248 | 81.404 |
| 8.402 | 96.151 |
| 6.862 | 76.141 |

# Totals
| user | cpu |
| ---- | ---- |
| 163.138 | 1825.809 |

# Averages
| user | cpu |
| ---- | ---- |
| 7.768 | 86.943 |
