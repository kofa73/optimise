perf: precompute interleaved PDE row order for each wavelet scale

Materialize the `dwt_interleave_rows(row, height, mult)` permutation once per scale and have `heat_PDE_diffusion` walk that array directly instead of recomputing the mapping on every pass. It keeps the current row traversal strategy that already benchmarked better than linear order, but removes repeated row-permutation arithmetic from every iteration and pairs naturally with prebuilt neighbour-row tables.
outcome: benchmark early abort: Benchmark early abort: 182.664s vs baseline 177.311s (-3.0%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.710 | 62.127 |
| 10.058 | 109.891 |
| 9.058 | 101.880 |
| 9.860 | 106.492 |
| 9.597 | 107.140 |
| 9.287 | 106.081 |
| 9.103 | 102.645 |
| 9.120 | 104.749 |
| 10.084 | 111.492 |
| 10.080 | 115.146 |
| 10.157 | 112.748 |
| 9.372 | 107.445 |
| 6.500 | 69.922 |
| 10.046 | 109.330 |
| 10.008 | 112.132 |
| 6.373 | 67.537 |
| 6.108 | 68.844 |
| 6.507 | 70.619 |
| 8.412 | 92.414 |
| 9.452 | 108.996 |
| 7.772 | 86.918 |

# Totals
| user | cpu |
| ---- | ---- |
| 182.664 | 2034.548 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.698 | 96.883 |
