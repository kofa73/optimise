perf: compute D (2cos²θ - 1) directly from spatial derivatives to eliminate accumulation math

In the gradient and Laplacian angle math, instead of computing and passing `cos²θ` into the accumulation loop where it undergoes the transformation `2.0f * cos_theta2 - 1.0f`, we can compute `D` directly as `(gx_sq - gy_sq) / mag_sq`. By exploiting this algebraic identity, we completely avoid computing a multiplication by 2.0 and a subtraction of 1.0 for every channel inside `accumulate_convolution_direct`, directly yielding the directional correction factor.
outcome: benchmark early abort: Benchmark early abort: 176.793s vs baseline 172.940s (-2.2%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 6.086 | 61.791 |
| 9.175 | 102.517 |
| 8.814 | 95.696 |
| 9.199 | 101.163 |
| 9.726 | 104.681 |
| 9.282 | 101.198 |
| 8.551 | 98.088 |
| 9.089 | 99.825 |
| 9.894 | 112.847 |
| 10.095 | 110.579 |
| 9.555 | 108.636 |
| 9.056 | 102.953 |
| 6.663 | 67.105 |
| 9.353 | 103.739 |
| 9.912 | 105.713 |
| 5.835 | 64.129 |
| 5.803 | 64.621 |
| 6.368 | 68.057 |
| 7.980 | 86.257 |
| 8.885 | 101.594 |
| 7.472 | 81.226 |

# Totals
| user | cpu |
| ---- | ---- |
| 176.793 | 1942.415 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.419 | 92.496 |
