remove 0.5f scaling from gradient/laplacian computation.

The factor cancels in angle ratios (cos²θ, sin²θ, cosθsinθ) and is absorbed into `half_anisotropy` (0.5 * anisotropy) for magnitude. Eliminates 4 float multiplies per pixel per channel.

outcome: target not reached

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.884 | 6.042 |
| 54.597 | 628.173 |
| 4.324 | 45.439 |
| 12.542 | 141.479 |
| 12.560 | 141.662 |
| 21.245 | 246.052 |
| 14.071 | 163.275 |
| 17.603 | 205.195 |
| 12.332 | 137.968 |
| 15.900 | 183.719 |
| 10.668 | 122.179 |
| 4.576 | 50.363 |
| 1.466 | 11.336 |
| 7.090 | 76.567 |
| 13.819 | 156.037 |
| 0.875 | 6.520 |
| 0.700 | 4.998 |
| 1.297 | 9.764 |
| 1.856 | 17.578 |
| 3.338 | 35.925 |
| 2.072 | 19.471 |

# Totals
| user | cpu |
| ---- | ---- |
| 213.815 | 2409.742 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.182 | 114.750 |
