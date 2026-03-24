perf: reuse pre-loaded HF_center and LF_center in final pixel integration

In the DIFFUSE_PIXEL_BODY macro, the final integration computes `acc[c] = HF[index + c] * strength + acc[c] / variance[c]` and `result[c] = fmaxf(acc[c] + LF[index + c], 0.f)`. Since `index == n4` (both equal `4 * (i * width + j)`), these loads are identical to `HF_center[c]` and `LF_center[c]` which were already loaded into local variables during the neighbor loading phase. Replace `HF[index + c]` with `HF_center[c]` and `LF[index + c]` with `LF_center[c]` to guarantee the compiler uses register-resident values instead of potentially re-fetching from memory. The proven pattern of replacing buffer indexing with pre-loaded scalars has yielded ~11.9% in prior experiments.
outcome: target not reached: 180.444s vs baseline 181.409s (+0.5%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.631 | 61.549 |
| 10.354 | 116.388 |
| 8.845 | 98.897 |
| 9.789 | 109.927 |
| 9.878 | 110.105 |
| 9.490 | 108.492 |
| 9.183 | 105.667 |
| 9.321 | 107.615 |
| 9.746 | 111.091 |
| 9.743 | 111.394 |
| 9.513 | 109.167 |
| 9.084 | 103.700 |
| 6.302 | 67.339 |
| 9.507 | 106.071 |
| 9.664 | 108.435 |
| 6.419 | 72.364 |
| 6.483 | 73.392 |
| 6.294 | 68.472 |
| 7.836 | 89.721 |
| 9.155 | 105.162 |
| 8.207 | 92.286 |

# Totals
| user | cpu |
| ---- | ---- |
| 180.444 | 2037.234 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.593 | 97.011 |
