perf: cache-block PDE solver in vertical column strips to fit 3-row stencil working set in L1 cache

The PDE solver's 9-point stencil accesses 3 rows (i-mult, i, i+mult) across the full image width. For a 6000-pixel-wide image, the 3-row neighborhood spans 3 × 6000 × 16 = 288KB, exceeding typical L1 cache (32-48KB). By processing vertical strips (e.g., 64-128 columns at a time), the working set shrinks to 3 × 128 × 16 = 6KB, fitting entirely in L1. Implement by adding an outer loop over column strips within the OMP parallel region, processing each strip's full row range before moving to the next. The per-pixel computation and SIMD vectorization remain unchanged; only the iteration order changes. This standard cache-blocking technique for stencil computations differs from failed "memory reordering" attempts (which changed data access order within a pixel body) by restructuring the iteration space at the tile level.
outcome: benchmark early abort: Benchmark early abort: 213.918s vs baseline 190.343s (-12.4%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.328 | 9.718 |
| 56.795 | 666.080 |
| 4.535 | 47.973 |
| 13.596 | 152.147 |
| 13.605 | 152.002 |
| 18.835 | 219.928 |
| 11.816 | 134.653 |
| 15.372 | 176.858 |
| 11.741 | 135.589 |
| 17.552 | 201.815 |
| 9.584 | 109.630 |
| 5.376 | 56.779 |
| 1.532 | 11.891 |
| 6.548 | 71.516 |
| 14.923 | 168.222 |
| 0.960 | 7.577 |
| 0.781 | 6.045 |
| 1.388 | 10.610 |
| 1.933 | 19.045 |
| 3.518 | 37.960 |
| 2.200 | 21.007 |

# Totals
| user | cpu |
| ---- | ---- |
| 213.918 | 2417.045 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.187 | 115.097 |
