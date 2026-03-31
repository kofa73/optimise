perf: precompute per-scale neighbour index tables for the CPU PDE stencil

Before entering the iteration loop, build `prev/center/next` row and column lookup tables for each `mult` used by `heat_PDE_diffusion`, with row entries already multiplied by `width` and optionally by `4`. That removes the per-pixel `MAX/MIN`, row-base multiplication, and repeated `4 * (...)` address formation from the hottest masked path without changing traversal order, convolution math, or OpenCL-only code.
outcome: benchmark early abort: Benchmark early abort: 183.163s vs baseline 177.311s (-3.3%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.717 | 62.072 |
| 9.926 | 108.107 |
| 9.084 | 102.118 |
| 9.857 | 106.391 |
| 9.596 | 106.835 |
| 9.764 | 107.941 |
| 9.019 | 104.293 |
| 9.274 | 106.714 |
| 10.092 | 111.350 |
| 10.229 | 116.881 |
| 10.310 | 114.410 |
| 9.503 | 108.838 |
| 6.818 | 71.077 |
| 9.817 | 109.727 |
| 10.007 | 111.847 |
| 6.243 | 66.208 |
| 5.999 | 67.639 |
| 6.632 | 72.086 |
| 8.320 | 91.241 |
| 9.362 | 107.789 |
| 7.594 | 84.825 |

# Totals
| user | cpu |
| ---- | ---- |
| 183.163 | 2038.389 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.722 | 97.066 |
