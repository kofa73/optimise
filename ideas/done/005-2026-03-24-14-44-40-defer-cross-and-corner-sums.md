perf: conditionally evaluate cross and corner sums to eliminate dead ALU

The symmetric pixel combinations `cross_corners` and `sum_corners` are currently computed unconditionally for both LF and HF buffers at the top of the pixel body. However, `sum_corners` is only ever consumed by the fully isotropic accumulation path, while `cross_corners` is exclusively used by the anisotropic (isophote/gradient) paths. By deferring the addition of these specific neighbor combinations to the control flow branches where they are actually used (or evaluating them lazily inside the accumulation step), we safely eliminate multiple redundant per-channel additions from the hot loop for all presets without introducing control flow dependencies, dropping dead ALU work and tightening register lifetimes.
outcome: target not reached: 172.821s vs baseline 172.940s (+0.1%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.618 | 61.240 |
| 9.058 | 102.230 |
| 8.836 | 97.613 |
| 9.101 | 101.464 |
| 9.058 | 101.101 |
| 8.841 | 100.823 |
| 8.471 | 98.142 |
| 8.701 | 99.739 |
| 9.748 | 110.359 |
| 9.695 | 110.344 |
| 9.400 | 108.160 |
| 9.007 | 103.048 |
| 6.300 | 67.667 |
| 9.394 | 105.452 |
| 9.677 | 108.029 |
| 5.681 | 63.506 |
| 5.705 | 64.505 |
| 6.301 | 68.462 |
| 7.851 | 89.245 |
| 9.144 | 105.690 |
| 7.234 | 80.735 |

# Totals
| user | cpu |
| ---- | ---- |
| 172.821 | 1947.554 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.230 | 92.741 |
