Swap sums and angle loop order.

Move the sums+variance `for_each_channel` loop (which loads all 18 LF+HF neighbor pixels) before the gradient/laplacian angle loop. After sums runs, all pixel values are in L1 cache, so the angle loop's re-loads of n1,n3,n5,n7 are guaranteed cache hits.

outcome: benchmark early abort: Benchmark early abort: 213.206s vs baseline 217.223s (+1.8%, need 3.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.928 | 6.204 |
| 53.412 | 627.180 |
| 4.227 | 44.728 |
| 12.794 | 144.170 |
| 12.689 | 143.787 |
| 21.307 | 249.873 |
| 14.204 | 165.989 |
| 17.684 | 207.088 |
| 12.234 | 141.671 |
| 15.997 | 186.604 |
| 10.806 | 124.455 |
| 4.600 | 50.875 |
| 1.439 | 11.418 |
| 7.111 | 77.368 |
| 13.922 | 158.057 |
| 0.825 | 6.477 |
| 0.669 | 4.977 |
| 1.271 | 9.923 |
| 1.804 | 17.640 |
| 3.257 | 35.346 |
| 2.026 | 19.526 |

# Totals
| user | cpu |
| ---- | ---- |
| 213.206 | 2433.356 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.153 | 115.874 |
