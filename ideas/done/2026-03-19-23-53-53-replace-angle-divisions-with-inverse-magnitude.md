perf: compute inverse magnitude to replace multiple divisions when finding angles

When determining `cos_grad` and `sin_grad`, the code currently performs two separate, high-latency floating-point divisions by `magnitude_grad`. By computing the reciprocal once (`inv_mag = 1.0f / magnitude_grad`) and using it to multiply the x and y derivatives (`grad_x * inv_mag`), we replace two divisions with one division and two fast multiplications. This eliminates up to 8 divisions per pixel in the critical path (4 channels × 2 orders).
outcome: benchmark early abort: Benchmark early abort: 222.841s vs baseline 217.223s (-2.6%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.905 | 5.952 |
| 57.221 | 658.896 |
| 4.430 | 46.873 |
| 12.900 | 145.291 |
| 13.205 | 145.168 |
| 22.149 | 253.324 |
| 14.767 | 167.536 |
| 18.113 | 210.949 |
| 12.511 | 140.417 |
| 16.697 | 188.891 |
| 10.989 | 126.236 |
| 4.952 | 51.479 |
| 1.513 | 11.612 |
| 7.345 | 79.864 |
| 14.639 | 162.201 |
| 0.931 | 7.353 |
| 0.734 | 5.556 |
| 1.319 | 10.140 |
| 1.934 | 18.854 |
| 3.443 | 37.243 |
| 2.144 | 20.551 |

# Totals
| user | cpu |
| ---- | ---- |
| 222.841 | 2494.386 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.611 | 118.780 |
