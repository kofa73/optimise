remove 0.5f central-difference scaling from gradient/laplacian computation.

The factor cancels in angle ratios (cos²θ = gx²/m²) and is absorbed into `half_anisotropy[k] = anisotropy[k] * 0.5f` precomputed outside the pixel loop. Saves 4 float multiplies per pixel per channel.

outcome: benchmark early abort: Benchmark early abort: 216.729s vs baseline 217.223s (+0.2%, need 2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.918 | 6.173 |
| 54.577 | 632.787 |
| 4.359 | 46.052 |
| 12.831 | 140.718 |
| 12.852 | 141.096 |
| 21.532 | 246.845 |
| 14.085 | 164.096 |
| 17.946 | 204.960 |
| 12.499 | 139.286 |
| 15.986 | 184.834 |
| 11.291 | 122.517 |
| 4.625 | 50.545 |
| 1.485 | 11.518 |
| 7.164 | 77.792 |
| 14.065 | 156.083 |
| 0.919 | 6.939 |
| 0.747 | 5.539 |
| 1.334 | 10.049 |
| 1.899 | 18.483 |
| 3.401 | 36.610 |
| 2.214 | 20.153 |

# Totals
| user | cpu |
| ---- | ---- |
| 216.729 | 2423.075 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.320 | 115.385 |
