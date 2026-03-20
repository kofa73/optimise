perf: bake 0.5f factor into cos_theta_sin_theta arrays to save inner-loop muls

In `accumulate_convolution_direct`, the cross-term `b11` computes `(c2 - 1.0f) * cos_theta_sin_theta * 0.5f`. Because this accumulation function is called up to 4 times per pixel, the `0.5f` multiplication is repeated needlessly. By multiplying `cos_grad * sin_grad` and `cos_lapl * sin_lapl` by `0.5f` immediately when they are calculated and stored in the `cos_theta_sin_theta` stack arrays, we can entirely eliminate the `0.5f` multiplication from the inner accumulation loops.
outcome: benchmark early abort: Benchmark early abort: 226.980s vs baseline 217.223s (-4.5%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.883 | 6.009 |
| 57.611 | 647.191 |
| 4.744 | 45.969 |
| 13.120 | 144.105 |
| 13.291 | 143.060 |
| 22.616 | 252.245 |
| 14.850 | 168.227 |
| 18.862 | 209.101 |
| 12.661 | 135.131 |
| 17.349 | 187.211 |
| 11.387 | 124.348 |
| 4.883 | 51.168 |
| 1.600 | 11.701 |
| 7.779 | 77.463 |
| 14.560 | 160.679 |
| 0.959 | 6.968 |
| 0.847 | 5.108 |
| 1.353 | 10.191 |
| 1.941 | 18.605 |
| 3.520 | 37.232 |
| 2.164 | 20.532 |

# Totals
| user | cpu |
| ---- | ---- |
| 226.980 | 2462.244 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.809 | 117.250 |
