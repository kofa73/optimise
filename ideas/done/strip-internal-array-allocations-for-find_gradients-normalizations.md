Strip internal array allocations for `find_gradients` normalizations

Strip internal array allocations for `find_gradients` normalizations, inlining arithmetic directly into native scalars inside `heat_PDE_diffusion`. Outcome during previous experiment (with different test data): **SUCCESS**. Reduced baseline from 45.631s to 40.958s (another ~10.2% drop).

outcome: improvement
commit: b7b4dfed32
Reduced sum(user) from 280.618s to 247.307s (~11.9% improvement)

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.268 | 9.814 |
| 57.697 | 652.385 |
| 4.768 | 48.858 |
| 15.134 | 166.161 |
| 15.087 | 166.520 |
| 26.442 | 299.086 |
| 17.629 | 198.476 |
| 21.953 | 248.522 |
| 12.644 | 139.694 |
| 19.796 | 223.692 |
| 13.348 | 148.686 |
| 5.707 | 61.353 |
| 1.748 | 14.060 |
| 7.771 | 82.231 |
| 15.160 | 167.233 |
| 0.972 | 7.325 |
| 0.783 | 5.837 |
| 1.587 | 12.481 |
| 1.975 | 18.772 |
| 3.606 | 37.490 |
| 2.232 | 20.835 |

# Totals
| user | cpu |
| ---- | ---- |
| 247.307 | 2729.511 |

# Averages
| user | cpu |
| ---- | ---- |
| 11.777 | 129.977 |
