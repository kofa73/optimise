Combine paired kernel convolutions to halve multiply-accumulate count

The inner loop builds 4 separate 9-element kernels and convolves each independently with neighbor pixels (4 x 9 = 36 MAC operations per channel). However, kern_first and kern_second both convolve against the same neighbour_pixel_LF data, and kern_third and kern_fourth both convolve against neighbour_pixel_HF. Instead of 4 separate convolutions, pre-combine the weighted kernels: combined_LF[k] = kern_first[k]*ABCD[0] + kern_second[k]*ABCD[1] and combined_HF[k] = kern_third[k]*ABCD[2] + kern_fourth[k]*ABCD[3], then perform only 2 convolutions (2 x 9 = 18 MACs). This also eliminates the separate 4-iteration accumulation loop for derivatives, cutting the convolution work nearly in half.
outcome: benchmark error

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.725 | 14.132 |
| 77.631 | 842.724 |
| 6.302 | 65.977 |
| 19.772 | 219.884 |
| 19.825 | 220.171 |
| 35.419 | 402.497 |
| 23.584 | 268.097 |
| 29.425 | 334.897 |
| 12.720 | 141.616 |
| 26.549 | 300.469 |
| 17.831 | 200.121 |
| 7.598 | 82.750 |
| 2.293 | 19.508 |
| 10.102 | 109.331 |
| 19.868 | 220.671 |
| 1.246 | 10.266 |
| 1.034 | 7.664 |
| 2.009 | 17.347 |
| 2.589 | 25.217 |
| 4.694 | 49.961 |
| 2.904 | 27.870 |

# Totals
| user | cpu |
| ---- | ---- |
| 325.120 | 3581.170 |

# Averages
| user | cpu |
| ---- | ---- |
| 15.482 | 170.532 |

outcome: not applicable
