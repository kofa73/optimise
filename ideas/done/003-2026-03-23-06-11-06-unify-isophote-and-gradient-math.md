perf: unify ISOPHOTE and GRADIENT accumulation by conditionally swapping axis sums

In `accumulate_convolution_direct`, the mathematical tensor for `DT_ISOTROPY_GRADIENT` is algebraically identical to `DT_ISOTROPY_ISOPHOTE` but with its axial weights (`a11` and `a22`) swapped and its cross-weight (`b11`) negated. By defining effective sums (`eff_sum_tb = (type == GRADIENT) ? sum_lr : sum_tb`, `eff_sum_lr = (type == GRADIENT) ? sum_tb : sum_lr`, and `eff_cross = (type == GRADIENT) ? -cross_corners : cross_corners`), we can eliminate the 3-case `switch` statement inside the inner loop and apply a single, unified ISOPHOTE formula. Since the isotropy type is passed uniformly, the compiler can lower the ternary swaps to static register blends, reducing code duplication and improving SIMD instruction cache density.
outcome: benchmark early abort: Benchmark early abort: 192.364s vs baseline 186.625s (-3.1%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 6.011 | 61.806 |
| 10.765 | 121.089 |
| 9.385 | 101.410 |
| 10.204 | 113.637 |
| 10.517 | 113.478 |
| 10.424 | 118.853 |
| 10.282 | 114.719 |
| 10.271 | 117.513 |
| 9.944 | 113.036 |
| 10.450 | 115.121 |
| 9.953 | 113.389 |
| 9.797 | 107.555 |
| 6.745 | 72.411 |
| 10.066 | 108.601 |
| 10.063 | 111.664 |
| 6.806 | 75.993 |
| 7.098 | 76.497 |
| 6.779 | 73.095 |
| 8.255 | 94.037 |
| 9.878 | 109.616 |
| 8.671 | 97.174 |

# Totals
| user | cpu |
| ---- | ---- |
| 192.364 | 2130.694 |

# Averages
| user | cpu |
| ---- | ---- |
| 9.160 | 101.462 |
