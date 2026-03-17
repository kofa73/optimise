Swap sums and angle loop order.

Move the sums+variance `for_each_channel` loop (which loads all 18 LF+HF neighbor pixels) before the gradient/laplacian angle loop. After sums runs, all pixel values are in L1 cache, so the angle loop's re-loads of n1,n3,n5,n7 are guaranteed cache hits.

outcome: benchmark early abort: Benchmark early abort: 218.245s vs baseline 217.223s (-0.5%, need 2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.915 | 6.119 |
| 54.478 | 630.594 |
| 4.578 | 44.010 |
| 12.759 | 144.533 |
| 13.048 | 143.824 |
| 21.847 | 251.462 |
| 14.261 | 166.159 |
| 18.230 | 208.719 |
| 12.547 | 137.893 |
| 16.192 | 188.350 |
| 11.195 | 124.061 |
| 4.677 | 51.205 |
| 1.505 | 11.601 |
| 7.514 | 77.495 |
| 13.999 | 158.946 |
| 0.887 | 6.793 |
| 0.731 | 5.422 |
| 1.327 | 10.025 |
| 1.861 | 17.941 |
| 3.623 | 35.045 |
| 2.071 | 19.662 |

# Totals
| user | cpu |
| ---- | ---- |
| 218.245 | 2439.859 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.393 | 116.184 |
