perf: use nontemporal stores for HF detail writes during bspline decomposition

Create a diffuse-local version of `decompose_2D_Bspline` that uses `copy_pixel_nontemporal` for writing HF detail coefficients (`HF[index + c] = in[index + c] - blur[c]`). The HF buffers are written once during decomposition and not read until the reconstruction pass, after ALL scales have been decomposed — the data is guaranteed to be evicted from cache before first read. Using nontemporal (streaming) stores avoids the read-for-ownership cache line fetch that normal stores require, halving the memory bandwidth consumed by HF writes. For a 24MP image with 8 effective scales and 16 iterations, this eliminates ~49 GB of unnecessary read bandwidth from write-allocate traffic. This follows the same proven pattern as the existing nontemporal output stores in the PDE solver (~1.3% gain), but targets a larger volume of data (HF writes happen once per scale vs. once for the final output). The local wrapper reuses the existing `_bspline_vertical_pass` and `_bspline_horizontal` helpers from bspline.h.
outcome: improvement
commit: 2930a4c304
Reduced sum(user) from 190.343s to 176.483s (~7.3% improvement)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.955 | 6.001 |
| 47.333 | 547.678 |
| 3.972 | 40.405 |
| 11.124 | 123.979 |
| 11.124 | 124.010 |
| 15.480 | 178.694 |
| 9.287 | 106.876 |
| 12.330 | 142.295 |
| 9.570 | 107.173 |
| 13.948 | 160.128 |
| 7.886 | 88.854 |
| 4.127 | 44.184 |
| 1.550 | 11.338 |
| 5.653 | 59.774 |
| 12.261 | 137.644 |
| 0.923 | 6.469 |
| 0.716 | 5.197 |
| 1.373 | 9.860 |
| 1.754 | 16.087 |
| 3.075 | 32.077 |
| 2.042 | 18.484 |

# Totals
| user | cpu |
| ---- | ---- |
| 176.483 | 1967.207 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.404 | 93.677 |
