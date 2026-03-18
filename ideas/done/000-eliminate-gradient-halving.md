remove 0.5f scaling factor from central difference gradients

The `find_gradients` function currently divides the central spatial differences by `2.0f`. This scaling factor is computationally unnecessary because it cancels out entirely when calculating the normalized `cos` and `sin` ratios (`gradient / magnitude`). While the gradient magnitude itself is also used in the exponential decay (`c2`), we can mathematically absorb this 2x relative scale difference by dividing the pre-computed `anisotropy` user parameters by 2.0f once outside the main loop. Removing the `0.5f` scaling eliminates two multiplications per channel per gradient/laplacian without altering the final mathematical result.

outcome: target not reached

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.875 | 6.019 |
| 56.035 | 646.262 |
| 4.381 | 45.757 |
| 12.621 | 142.822 |
| 12.739 | 142.402 |
| 21.520 | 247.334 |
| 14.134 | 163.646 |
| 17.675 | 205.895 |
| 12.275 | 137.464 |
| 15.944 | 184.462 |
| 10.739 | 122.635 |
| 4.583 | 49.625 |
| 1.459 | 11.456 |
| 7.239 | 77.787 |
| 14.099 | 159.084 |
| 0.885 | 6.780 |
| 0.713 | 5.312 |
| 1.302 | 9.661 |
| 1.842 | 17.811 |
| 3.401 | 36.057 |
| 2.111 | 20.189 |

# Totals
| user | cpu |
| ---- | ---- |
| 216.572 | 2438.460 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.313 | 116.117 |
