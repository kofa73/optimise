Remove 0.5f central-difference scaling from gradient/laplacian computation.

The factor cancels in angle ratios (cos²θ = gx²/m²) and is absorbed into `half_anisotropy[k] = anisotropy[k] * 0.5f` precomputed outside the pixel loop. Saves 4 float multiplies per pixel per channel.

outcome: benchmark early abort: Benchmark early abort: 226.403s vs baseline 231.975s (+2.4%, need 5.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.033 | 7.978 |
| 53.821 | 631.001 |
| 4.368 | 45.772 |
| 13.827 | 156.662 |
| 13.803 | 156.850 |
| 23.882 | 280.772 |
| 15.847 | 185.654 |
| 19.846 | 233.163 |
| 12.239 | 141.920 |
| 17.925 | 209.734 |
| 12.034 | 139.089 |
| 5.124 | 57.174 |
| 1.566 | 12.713 |
| 7.058 | 76.986 |
| 13.790 | 156.754 |
| 0.859 | 6.701 |
| 0.700 | 5.229 |
| 1.385 | 11.145 |
| 1.857 | 18.199 |
| 3.359 | 36.357 |
| 2.080 | 20.141 |

# Totals
| user | cpu |
| ---- | ---- |
| 226.403 | 2589.994 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.781 | 123.333 |
