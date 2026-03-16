remove 0.5f central-difference scaling from gradient/laplacian computation.

The factor cancels in angle ratios (cos²θ = gx²/m²) and is absorbed into `half_anisotropy[k] = anisotropy[k] * 0.5f` precomputed outside the pixel loop. Saves 4 float multiplies per pixel per channel.

outcome: benchmark early abort: Benchmark early abort: 212.162s vs baseline 217.223s (+2.3%, need 3.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.885 | 6.164 |
| 53.655 | 634.034 |
| 4.347 | 46.218 |
| 12.512 | 141.235 |
| 12.570 | 141.648 |
| 21.007 | 246.177 |
| 13.975 | 163.254 |
| 17.505 | 204.864 |
| 12.249 | 141.840 |
| 15.779 | 184.008 |
| 10.628 | 122.492 |
| 4.546 | 50.211 |
| 1.460 | 11.529 |
| 7.131 | 77.570 |
| 13.899 | 157.543 |
| 0.843 | 6.602 |
| 0.664 | 5.156 |
| 1.273 | 9.824 |
| 1.821 | 18.006 |
| 3.349 | 36.228 |
| 2.064 | 20.049 |

# Totals
| user | cpu |
| ---- | ---- |
| 212.162 | 2424.652 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.103 | 115.460 |
