Rewrite the 9-element `kernel` matrix instantiation

Rewrite the 9-element `kernel` matrix instantiation with inline algebraically reduced scalar permutations (removing `compute_kernel` and `build_matrix` overheads). Outcome during previous experiment (with different test data): **SUCCESS**. Reduced baseline from 49.775s to 45.631s.

outcome: benchmark early abort: obvious regression

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.301 | 9.886 |
| 57.249 | 651.557 |
| 4.989 | 50.095 |
| 15.098 | 166.127 |
| 15.038 | 166.138 |
| 26.435 | 299.308 |
| 17.634 | 199.173 |
| 21.935 | 248.645 |
| 12.672 | 141.157 |
| 19.832 | 223.384 |
| 13.302 | 148.939 |
| 5.720 | 61.184 |
| 1.776 | 14.220 |
| 7.822 | 82.465 |
| 15.252 | 167.942 |
| 0.977 | 7.693 |
| 0.788 | 5.773 |
| 1.598 | 12.357 |
| 2.014 | 19.134 |
| 3.618 | 37.512 |
| 2.258 | 20.840 |

# Totals
| user | cpu |
| ---- | ---- |
| 247.308 | 2733.529 |

# Averages
| user | cpu |
| ---- | ---- |
| 11.777 | 130.168 |

outcome: not applicable
