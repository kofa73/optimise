perf: initialize masked inpaint by bulk copy plus sparse overwrite

Rewrite `inpaint_mask` to first copy `original` into `inpainted` in one bulk pass, then iterate only over masked pixel indices gathered while building the highlight mask and overwrite those pixels with the seeded noise values. This preserves behavior but turns initialization for sparse clipped highlights from a branch-heavy full-image loop into mostly a contiguous copy plus sparse work.

outcome: target not reached: 167.003s vs baseline 167.053s (+0.5%, need 3.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.669 | 61.192 |
| 9.486 | 105.573 |
| 8.993 | 101.119 |
| 9.262 | 102.611 |
| 9.228 | 102.688 |
| 9.073 | 103.788 |
| 8.721 | 100.518 |
| 8.897 | 102.240 |
| 0.040 | 0.246 |
| 9.875 | 111.415 |
| 9.543 | 109.452 |
| 9.081 | 103.824 |
| 6.405 | 68.144 |
| 9.624 | 108.045 |
| 9.947 | 110.085 |
| 5.871 | 65.412 |
| 5.909 | 66.620 |
| 6.424 | 69.153 |
| 8.068 | 91.953 |
| 9.389 | 108.277 |
| 7.498 | 83.491 |

# Totals
| user | cpu |
| ---- | ---- |
| 167.003 | 1875.846 |

# Averages
| user | cpu |
| ---- | ---- |
| 7.953 | 89.326 |
