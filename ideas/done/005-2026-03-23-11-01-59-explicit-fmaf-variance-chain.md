perf: use explicit fmaf() chains for variance sum-of-squares accumulation

The variance computation `sqf(hf0) + sqf(hf1) + ... + sqf(hf8)` expands to 9 multiplications and 8 additions. On FMA-capable hardware, these can be fused into 8 FMA instructions + 1 multiply, nearly halving the micro-op count for this computation. While the compiler may generate FMAs with `-ffast-math`, without it the C standard forbids this fusion (due to different rounding). Rewrite the variance as an explicit `fmaf(hf0, hf0, fmaf(hf1, hf1, ...))` chain to guarantee FMA usage regardless of compiler flags. The variance is computed for every pixel unconditionally and represents a significant fraction of per-pixel ALU in the fully isotropic case, where angle/exp computations are skipped.
outcome: benchmark early abort: Benchmark early abort: 185.378s vs baseline 181.409s (-2.2%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.696 | 62.097 |
| 10.344 | 117.719 |
| 9.221 | 100.250 |
| 10.064 | 113.246 |
| 10.415 | 113.310 |
| 9.625 | 110.702 |
| 9.588 | 107.238 |
| 9.480 | 109.609 |
| 9.838 | 111.907 |
| 10.152 | 114.821 |
| 9.803 | 112.905 |
| 9.642 | 106.582 |
| 6.392 | 69.075 |
| 9.855 | 107.255 |
| 9.734 | 109.150 |
| 6.462 | 73.029 |
| 6.889 | 74.199 |
| 6.403 | 69.847 |
| 7.959 | 90.959 |
| 9.525 | 105.893 |
| 8.291 | 93.481 |

# Totals
| user | cpu |
| ---- | ---- |
| 185.378 | 2073.274 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.828 | 98.727 |
