remove 0.5f scaling from gradient/laplacian computation.

The factor cancels in angle ratios (cos²θ, sin²θ, cosθsinθ) and is absorbed into `half_anisotropy` (0.5 * anisotropy) for magnitude. Eliminates 4 float multiplies per pixel per channel.

outcome: benchmark early abort: Benchmark early abort: 211.985s vs baseline 217.223s (+2.4%, need 3.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.903 | 6.017 |
| 53.636 | 633.794 |
| 4.309 | 45.738 |
| 12.481 | 141.508 |
| 12.478 | 141.789 |
| 21.141 | 247.698 |
| 13.950 | 163.142 |
| 17.450 | 204.435 |
| 12.235 | 141.797 |
| 15.920 | 185.478 |
| 10.629 | 122.553 |
| 4.531 | 50.128 |
| 1.459 | 11.559 |
| 7.135 | 77.907 |
| 13.763 | 157.105 |
| 0.842 | 6.636 |
| 0.669 | 5.167 |
| 1.271 | 9.785 |
| 1.821 | 18.170 |
| 3.312 | 36.117 |
| 2.050 | 19.966 |

# Totals
| user | cpu |
| ---- | ---- |
| 211.985 | 2426.489 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.095 | 115.547 |
