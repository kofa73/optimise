Swap sums and angle loop order.

Move the sums+variance `for_each_channel` loop (which loads all 18 LF+HF neighbor pixels) before the gradient/laplacian angle loop. After sums runs, all pixel values are in L1 cache, so the angle loop's re-loads of n1,n3,n5,n7 are guaranteed cache hits.

outcome: target not reached: 215.096s vs baseline 215.280s (+0.1%, need 2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.884 | 5.986 |
| 53.813 | 616.647 |
| 4.207 | 43.794 |
| 12.796 | 143.413 |
| 12.790 | 143.007 |
| 21.749 | 248.714 |
| 14.510 | 164.534 |
| 17.863 | 206.612 |
| 12.314 | 135.543 |
| 16.341 | 185.294 |
| 10.783 | 123.452 |
| 4.624 | 50.033 |
| 1.456 | 11.276 |
| 7.124 | 75.947 |
| 13.920 | 155.641 |
| 0.853 | 6.555 |
| 0.688 | 4.866 |
| 1.290 | 9.729 |
| 1.805 | 17.374 |
| 3.259 | 34.410 |
| 2.027 | 19.203 |

# Totals
| user | cpu |
| ---- | ---- |
| 215.096 | 2402.030 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.243 | 114.382 |
