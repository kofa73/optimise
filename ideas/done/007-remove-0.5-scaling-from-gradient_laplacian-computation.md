remove 0.5f scaling from gradient/laplacian computation.

The factor cancels in angle ratios (cos²θ, sin²θ, cosθsinθ) and is absorbed into `half_anisotropy` (0.5 * anisotropy) for magnitude. Eliminates 4 float multiplies per pixel per channel.

outcome: benchmark early abort: Benchmark early abort: 216.592s vs baseline 217.223s (+0.3%, need 2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.915 | 6.100 |
| 54.505 | 632.199 |
| 4.627 | 44.447 |
| 12.571 | 142.030 |
| 12.869 | 141.299 |
| 21.541 | 247.737 |
| 14.076 | 164.189 |
| 17.965 | 205.436 |
| 12.560 | 138.003 |
| 16.006 | 185.814 |
| 11.033 | 122.395 |
| 4.602 | 50.502 |
| 1.488 | 11.406 |
| 7.278 | 77.776 |
| 13.971 | 156.925 |
| 0.917 | 7.032 |
| 0.749 | 5.542 |
| 1.321 | 9.910 |
| 1.898 | 18.395 |
| 3.533 | 35.933 |
| 2.167 | 19.966 |

# Totals
| user | cpu |
| ---- | ---- |
| 216.592 | 2423.036 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.314 | 115.383 |
