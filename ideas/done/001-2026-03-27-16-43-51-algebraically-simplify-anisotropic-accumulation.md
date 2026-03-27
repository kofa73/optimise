perf: rewrite anisotropic accumulation to save inner-loop multiplications

By expanding the `alpha` and `beta` blending weights in `accumulate_convolution_direct`, we can algebraically simplify the accumulation from `abcd * (0.5 * (1+c2) * iso + 0.5 * (1-c2) * dir)` to `(abcd * 0.5) * ((iso + dir) + c2 * (iso - dir))` for the ISOPHOTE path, and `(abcd * 0.5) * ((iso - dir) + c2 * (iso + dir))` for the GRADIENT path. This mathematically identical formulation exploits symmetry to eliminate 3 floating-point multiplications per channel for every anisotropic convolution, replacing them with cheaper additions.
outcome: benchmark early abort: Benchmark early abort: 185.485s vs baseline 172.940s (-7.3%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.971 | 61.608 |
| 9.746 | 104.991 |
| 9.403 | 97.826 |
| 9.433 | 101.507 |
| 9.907 | 101.022 |
| 9.302 | 102.258 |
| 9.159 | 100.379 |
| 9.559 | 101.713 |
| 10.428 | 104.719 |
| 11.548 | 107.006 |
| 11.180 | 106.272 |
| 9.520 | 102.739 |
| 6.444 | 67.341 |
| 9.937 | 105.626 |
| 9.911 | 109.436 |
| 5.871 | 64.692 |
| 6.180 | 65.216 |
| 6.426 | 68.415 |
| 8.076 | 90.944 |
| 9.732 | 106.442 |
| 7.752 | 82.091 |

# Totals
| user | cpu |
| ---- | ---- |
| 185.485 | 1952.243 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.833 | 92.964 |
