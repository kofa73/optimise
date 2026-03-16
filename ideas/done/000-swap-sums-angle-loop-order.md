Swap sums and angle loop order.

Move the sums+variance `for_each_channel` loop (which loads all 18 LF+HF neighbor pixels) before the gradient/laplacian angle loop. After sums runs, all pixel values are in L1 cache, so the angle loop's re-loads of n1,n3,n5,n7 are guaranteed cache hits.


outcome: benchmark early abort: Benchmark early abort: 223.761s vs baseline 231.975s (+3.5%, need 5.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.072 | 8.366 |
| 53.311 | 626.043 |
| 4.262 | 45.018 |
| 13.836 | 156.893 |
| 13.787 | 156.813 |
| 23.377 | 274.495 |
| 15.541 | 181.989 |
| 19.418 | 227.932 |
| 12.233 | 141.634 |
| 17.585 | 205.481 |
| 11.825 | 136.414 |
| 5.010 | 55.797 |
| 1.577 | 12.842 |
| 7.092 | 77.200 |
| 13.906 | 157.704 |
| 0.845 | 6.459 |
| 0.657 | 5.043 |
| 1.385 | 11.149 |
| 1.791 | 17.512 |
| 3.241 | 35.238 |
| 2.010 | 19.444 |

# Totals
| user | cpu |
| ---- | ---- |
| 223.761 | 2559.466 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.655 | 121.879 |
