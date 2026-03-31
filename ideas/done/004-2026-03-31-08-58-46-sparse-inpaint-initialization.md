perf: initialize masked inpaint by bulk copy plus sparse overwrite

Rewrite `inpaint_mask` to first copy `original` into `inpainted` in one bulk pass, then iterate only over masked pixel indices gathered while building the highlight mask and overwrite those pixels with the seeded noise values. This preserves behavior but turns initialization for sparse clipped highlights from a branch-heavy full-image loop into mostly a contiguous copy plus sparse work.
outcome: target not reached: 176.974s vs baseline 177.311s (-0.1%, need 5.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.664 | 60.897 |
| 9.463 | 106.810 |
| 9.061 | 100.238 |
| 9.275 | 103.075 |
| 9.289 | 103.330 |
| 8.988 | 101.855 |
| 8.547 | 98.601 |
| 8.841 | 100.362 |
| 9.863 | 111.314 |
| 9.979 | 113.234 |
| 9.724 | 110.995 |
| 9.213 | 105.409 |
| 6.364 | 67.943 |
| 9.605 | 107.729 |
| 9.830 | 108.674 |
| 5.964 | 66.223 |
| 5.961 | 67.001 |
| 6.344 | 68.256 |
| 8.058 | 91.298 |
| 9.375 | 107.968 |
| 7.566 | 83.937 |

# Totals
| user | cpu |
| ---- | ---- |
| 176.974 | 1985.149 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.427 | 94.531 |
