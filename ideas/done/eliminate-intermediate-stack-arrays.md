Eliminate `neighbour_pixel_HF[9]` and `neighbour_pixel_LF[9]` intermediate stack arrays entirely

Eliminate `neighbour_pixel_HF[9]` and `neighbour_pixel_LF[9]` intermediate stack arrays entirely, computing gradients, sums, and variance directly from HF/LF source pointers using pre-computed n0-n8 offsets. Avoids 72 float writes + reads from stack, leveraging L1 cache spatial locality.


outcome: benchmark early abort: obvious regression

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.258 | 9.357 |
| 56.913 | 608.602 |
| 4.517 | 45.961 |
| 14.361 | 150.470 |
| 14.504 | 149.968 |
| 25.963 | 278.384 |
| 16.720 | 188.707 |
| 20.830 | 235.149 |
| 12.678 | 141.033 |
| 18.840 | 211.900 |
| 12.712 | 141.481 |
| 5.516 | 58.141 |
| 1.660 | 12.835 |
| 7.288 | 76.389 |
| 14.257 | 156.308 |
| 0.959 | 7.111 |
| 0.823 | 5.654 |
| 1.510 | 11.534 |
| 1.990 | 18.072 |
| 3.549 | 36.393 |
| 2.168 | 19.981 |

# Totals
| user | cpu |
| ---- | ---- |
| 239.016 | 2563.430 |

# Averages
| user | cpu |
| ---- | ---- |
| 11.382 | 122.068 |
