perf: use halo-padded CPU PDE buffers to make the isotropic interior loop branch-free

For the CPU `process` path only, allocate a small replicated border around each working image (or per-row scratch halo) and populate it once per iteration so the hot PDE loop can address neighbors with fixed offsets and no coordinate clamping or border conditionals. This differs from border peeling and split-kernel approaches because the main loop stays single-path and readable while deleting both x and y boundary math from the overwhelming majority of pixels. Given the strong results from removing hot-loop clamp work, a halo-based interior path is a plausible next step for the full-frame, no-mask normal preset.
outcome: benchmark early abort: Benchmark early abort: 169.599s vs baseline 159.638s (-6.2%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.862 | 63.918 |
| 10.377 | 113.156 |
| 7.256 | 80.524 |
| 9.418 | 103.831 |
| 9.493 | 103.799 |
| 9.987 | 114.033 |
| 10.015 | 111.027 |
| 9.857 | 113.071 |
| 0.041 | 0.257 |
| 11.243 | 124.446 |
| 10.634 | 121.989 |
| 10.513 | 116.095 |
| 6.480 | 69.679 |
| 10.100 | 111.322 |
| 8.632 | 94.835 |
| 5.525 | 61.169 |
| 5.533 | 62.022 |
| 7.008 | 72.336 |
| 6.686 | 75.841 |
| 7.740 | 88.558 |
| 7.199 | 76.299 |

# Totals
| user | cpu |
| ---- | ---- |
| 169.599 | 1878.207 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.076 | 89.438 |
