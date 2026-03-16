remove 0.5f scaling factor from central difference gradients

The `find_gradients` function currently divides the central spatial differences by `2.0f`. This scaling factor is computationally unnecessary because it cancels out entirely when calculating the normalized `cos` and `sin` ratios (`gradient / magnitude`). While the gradient magnitude itself is also used in the exponential decay (`c2`), we can mathematically absorb this 2x relative scale difference by dividing the pre-computed `anisotropy` user parameters by 2.0f once outside the main loop. Removing the `0.5f` scaling eliminates two multiplications per channel per gradient/laplacian without altering the final mathematical result.
outcome: benchmark early abort: Benchmark early abort: 232.092s vs baseline 231.975s (-0.1%, need 5.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.101 | 8.512 |
| 55.389 | 650.008 |
| 4.396 | 46.345 |
| 14.309 | 161.347 |
| 14.296 | 161.868 |
| 24.345 | 284.981 |
| 16.258 | 189.711 |
| 20.281 | 237.059 |
| 12.294 | 141.981 |
| 18.292 | 212.868 |
| 12.352 | 142.432 |
| 5.238 | 58.130 |
| 1.633 | 13.209 |
| 7.309 | 79.237 |
| 14.145 | 160.262 |
| 0.894 | 6.995 |
| 0.720 | 5.448 |
| 1.429 | 11.386 |
| 1.900 | 18.588 |
| 3.401 | 36.752 |
| 2.110 | 20.281 |

# Totals
| user | cpu |
| ---- | ---- |
| 232.092 | 2647.400 |

# Averages
| user | cpu |
| ---- | ---- |
| 11.052 | 126.067 |
