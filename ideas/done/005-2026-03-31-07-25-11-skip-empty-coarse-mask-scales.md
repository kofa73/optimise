perf: skip whole coarse scales when the downsampled inpaint mask becomes empty

After generating the per-scale mask, detect scales whose padded active region is empty and bypass their decomposition, PDE, and reconstruction work entirely. Sparse highlight masks often disappear on upper wavelet levels, so this turns a masked inpaint preset into fewer full-image passes rather than a faster version of the same passes, which is usually a better trade for this file’s performance profile.
outcome: target not reached: 176.994s vs baseline 177.311s (+0.1%, need 5.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.671 | 60.987 |
| 9.530 | 106.710 |
| 8.946 | 100.616 |
| 9.336 | 103.131 |
| 9.276 | 103.114 |
| 9.006 | 101.960 |
| 8.563 | 98.808 |
| 8.784 | 100.774 |
| 9.842 | 111.190 |
| 9.925 | 113.449 |
| 9.746 | 111.108 |
| 9.229 | 105.449 |
| 6.377 | 68.006 |
| 9.650 | 106.912 |
| 9.786 | 109.313 |
| 5.964 | 66.008 |
| 5.947 | 67.018 |
| 6.377 | 69.082 |
| 8.128 | 91.442 |
| 9.367 | 107.787 |
| 7.544 | 84.272 |

# Totals
| user | cpu |
| ---- | ---- |
| 176.994 | 1987.136 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.428 | 94.626 |
