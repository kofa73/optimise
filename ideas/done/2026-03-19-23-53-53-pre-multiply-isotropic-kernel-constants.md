perf: pre-multiply isotropic kernel constants by abcd speed factors

For isotropic diffusion, the accumulation loop calculates a weighted sum of neighbors using constants `0.25f`, `0.5f`, and `-3.f`, and then multiplies the total sum by `abcd`. By distributing `abcd` into the constants before the row loop (`w_corner = abcd * 0.25f`, etc.), we can apply these pre-scaled weights directly to the pixel sums. This removes the outer `abcd * (...)` multiplication from the innermost loop, saving 1 multiply per channel for all isotropic orders.
outcome: benchmark early abort: Benchmark early abort: 224.305s vs baseline 217.223s (-3.3%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.889 | 6.130 |
| 56.282 | 649.716 |
| 4.530 | 47.685 |
| 13.303 | 147.894 |
| 13.173 | 148.540 |
| 22.561 | 258.160 |
| 15.049 | 170.888 |
| 18.740 | 214.377 |
| 12.389 | 142.118 |
| 16.972 | 192.747 |
| 11.528 | 127.889 |
| 4.784 | 52.628 |
| 1.510 | 11.942 |
| 7.407 | 80.866 |
| 14.714 | 162.881 |
| 0.920 | 7.134 |
| 0.733 | 5.582 |
| 1.330 | 10.213 |
| 1.917 | 18.637 |
| 3.433 | 37.120 |
| 2.141 | 20.540 |

# Totals
| user | cpu |
| ---- | ---- |
| 224.305 | 2513.687 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.681 | 119.699 |
