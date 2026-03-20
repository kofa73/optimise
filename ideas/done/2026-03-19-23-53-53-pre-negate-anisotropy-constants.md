perf: pre-negate anisotropy constants to eliminate inner-loop unary negations

The exponents for the diffusion tensor are computed per-pixel using `c2[k] = -magnitude * anisotropy[k]`. Since `anisotropy` is constant for the entire pass, we can pre-negate these array values once outside the main loop (`neg_anisotropy[k] = -anisotropy[k]`). This replaces the inner-loop computation with a direct multiplication (`magnitude * neg_anisotropy[k]`), stripping an unnecessary floating-point sign flip from the core gradient pass.
outcome: target not reached: 219.628s vs baseline 217.223s (-1.1%, need 2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.886 | 5.926 |
| 55.612 | 641.683 |
| 4.446 | 46.459 |
| 12.966 | 144.789 |
| 12.878 | 145.331 |
| 22.074 | 253.267 |
| 14.554 | 167.526 |
| 18.388 | 211.551 |
| 12.359 | 138.259 |
| 16.357 | 189.241 |
| 11.073 | 125.724 |
| 4.716 | 50.984 |
| 1.499 | 11.599 |
| 7.249 | 78.064 |
| 14.177 | 159.191 |
| 0.909 | 7.044 |
| 0.718 | 5.434 |
| 1.332 | 9.919 |
| 1.862 | 18.007 |
| 3.438 | 36.369 |
| 2.135 | 20.445 |

# Totals
| user | cpu |
| ---- | ---- |
| 219.628 | 2466.812 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.458 | 117.467 |
