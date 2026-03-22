perf: replace i_neighbours[3] array with 3 named scalar variables for row offsets

The `i_neighbours[3]` array stores the three row offset products (above, center, below) and is accessed 9 times within the pixel body to compute neighbor addresses. Replace it with three named scalar variables `row_above`, `row_center`, `row_below`. While the compiler may already map a 3-element array to registers, the explicit scalar declaration follows the proven "intermediate stack arrays → native scalar variables" optimization pattern that has consistently yielded improvements (~6-12% in prior experiments). Named scalars give the compiler clearer aliasing guarantees and eliminate any array-indexing overhead, which matters given this code is inside the hottest loop of the module.
outcome: benchmark early abort: Benchmark early abort: 214.011s vs baseline 200.347s (-6.8%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.899 | 5.734 |
| 53.649 | 606.973 |
| 4.411 | 44.195 |
| 12.934 | 138.304 |
| 12.855 | 139.821 |
| 21.268 | 235.740 |
| 14.029 | 155.536 |
| 17.643 | 193.725 |
| 10.916 | 125.289 |
| 16.814 | 183.212 |
| 10.931 | 116.546 |
| 4.763 | 50.188 |
| 1.493 | 10.993 |
| 6.803 | 70.859 |
| 14.019 | 151.650 |
| 0.916 | 6.954 |
| 0.767 | 5.452 |
| 1.368 | 9.731 |
| 1.926 | 17.823 |
| 3.464 | 35.674 |
| 2.143 | 19.464 |

# Totals
| user | cpu |
| ---- | ---- |
| 214.011 | 2323.863 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.191 | 110.660 |
