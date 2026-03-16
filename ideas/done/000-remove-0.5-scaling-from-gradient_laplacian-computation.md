Remove 0.5f scaling from gradient/laplacian computation. The factor cancels in angle ratios (cos²θ, sin²θ, cosθsinθ) and is absorbed into `half_anisotropy` (0.5 * anisotropy) for magnitude. Eliminates 4 float multiplies per pixel per channel.

outcome: benchmark early abort: Benchmark early abort: 226.282s vs baseline 231.975s (+2.5%, need 5.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.078 | 8.405 |
| 53.344 | 630.606 |
| 4.334 | 46.025 |
| 13.844 | 157.945 |
| 13.783 | 157.152 |
| 23.776 | 279.529 |
| 15.847 | 185.180 |
| 20.387 | 237.086 |
| 12.256 | 142.192 |
| 17.867 | 209.145 |
| 11.999 | 138.737 |
| 5.114 | 57.130 |
| 1.559 | 12.934 |
| 7.136 | 77.660 |
| 13.821 | 156.973 |
| 0.870 | 6.851 |
| 0.676 | 5.042 |
| 1.394 | 11.153 |
| 1.823 | 17.848 |
| 3.322 | 36.151 |
| 2.052 | 19.998 |

# Totals
| user | cpu |
| ---- | ---- |
| 226.282 | 2593.742 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.775 | 123.512 |
