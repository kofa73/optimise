Swap sums and angle loop order.

Move the sums+variance `for_each_channel` loop (which loads all 18 LF+HF neighbor pixels) before the gradient/laplacian angle loop. After sums runs, all pixel values are in L1 cache, so the angle loop's re-loads of n1,n3,n5,n7 are guaranteed cache hits.

outcome: target not reached

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.884 | 6.003 |
| 54.028 | 627.213 |
| 4.328 | 44.005 |
| 12.742 | 144.347 |
| 12.983 | 143.502 |
| 21.778 | 250.826 |
| 14.195 | 165.861 |
| 18.128 | 207.705 |
| 12.489 | 137.970 |
| 16.134 | 187.388 |
| 10.874 | 124.239 |
| 4.642 | 51.157 |
| 1.472 | 11.359 |
| 7.290 | 76.543 |
| 13.952 | 158.381 |
| 0.877 | 6.648 |
| 0.703 | 5.219 |
| 1.304 | 9.890 |
| 1.835 | 17.701 |
| 3.489 | 34.714 |
| 2.047 | 19.515 |

# Totals
| user | cpu |
| ---- | ---- |
| 216.174 | 2430.186 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.294 | 115.723 |
