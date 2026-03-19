remove 0.5f central-difference scaling from gradient/laplacian computation.

The factor cancels in angle ratios (cos²θ = gx²/m²) and is absorbed into `half_anisotropy[k] = anisotropy[k] * 0.5f` precomputed outside the pixel loop. Saves 4 float multiplies per pixel per channel.

outcome: target not reached

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.895 | 6.041 |
| 54.208 | 631.532 |
| 4.344 | 45.891 |
| 12.750 | 140.925 |
| 12.557 | 141.513 |
| 21.352 | 247.467 |
| 14.089 | 163.595 |
| 17.913 | 205.254 |
| 12.298 | 139.615 |
| 15.948 | 184.775 |
| 11.007 | 122.308 |
| 4.564 | 50.214 |
| 1.456 | 11.453 |
| 7.096 | 77.484 |
| 14.095 | 155.872 |
| 0.884 | 6.809 |
| 0.699 | 5.257 |
| 1.293 | 9.785 |
| 1.870 | 18.263 |
| 3.344 | 36.123 |
| 2.081 | 19.950 |

# Totals
| user | cpu |
| ---- | ---- |
| 214.743 | 2420.126 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.226 | 115.244 |
