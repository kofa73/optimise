perf: reuse identical gradient and laplacian kernels across matched order pairs

When two orders have the same anisotropy factor and isotropy mode, build the local kernel once and reuse it for both consumers instead of calling `compute_kernel()` twice. In the strong instance, orders 1 and 3 share the same gradient-driven kernel, and orders 2 and 4 share the same laplacian-driven kernel, so this removes duplicate per-pixel kernel construction without the register-pressure risk of fully fusing the later convolution loops.
outcome: benchmark early abort: Benchmark early abort: 340.211s vs baseline 163.578s (-108.0%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 6.003 | 61.243 |
| 19.345 | 220.340 |
| 18.158 | 209.497 |
| 20.935 | 236.746 |
| 21.036 | 238.020 |
| 19.316 | 221.591 |
| 18.671 | 215.278 |
| 19.204 | 220.781 |
| 0.039 | 0.247 |
| 20.058 | 230.170 |
| 19.621 | 225.449 |
| 18.666 | 215.081 |
| 14.418 | 163.318 |
| 21.036 | 237.857 |
| 21.871 | 247.907 |
| 11.239 | 125.154 |
| 11.192 | 127.035 |
| 14.567 | 161.629 |
| 13.955 | 162.231 |
| 16.652 | 190.470 |
| 14.229 | 159.495 |

# Totals
| user | cpu |
| ---- | ---- |
| 340.211 | 3869.539 |

# Averages
| user | cpu |
| ---- | ---- |
| 16.201 | 184.264 |
