Swap sums and angle loop order.

Move the sums+variance `for_each_channel` loop (which loads all 18 LF+HF neighbor pixels) before the gradient/laplacian angle loop. After sums runs, all pixel values are in L1 cache, so the angle loop's re-loads of n1,n3,n5,n7 are guaranteed cache hits.

outcome: benchmark early abort: Benchmark early abort: 194.985s vs baseline 188.886s (-3.2%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.848 | 63.203 |
| 10.771 | 117.580 |
| 8.978 | 100.102 |
| 10.848 | 117.633 |
| 10.621 | 118.145 |
| 11.137 | 123.476 |
| 10.420 | 120.093 |
| 10.929 | 121.946 |
| 9.915 | 113.155 |
| 10.855 | 119.665 |
| 10.381 | 117.770 |
| 10.114 | 111.594 |
| 6.975 | 75.259 |
| 9.843 | 109.797 |
| 10.367 | 111.934 |
| 6.706 | 74.413 |
| 6.691 | 75.343 |
| 7.274 | 75.511 |
| 8.140 | 92.171 |
| 9.689 | 107.662 |
| 8.483 | 94.449 |

# Totals
| user | cpu |
| ---- | ---- |
| 194.985 | 2160.901 |

# Averages
| user | cpu |
| ---- | ---- |
| 9.285 | 102.900 |
