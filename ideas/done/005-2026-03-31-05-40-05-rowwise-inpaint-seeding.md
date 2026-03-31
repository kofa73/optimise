perf: rewrite inpaint_mask as row-wise masked seeding without flat-index divides

Rework `inpaint_mask()` into nested row/column loops and seed noise only for masked spans, so it no longer derives coordinates from a flat `k` index with per-pixel division/modulo and full-frame branching. The gain is smaller than the PDE-path ideas, but this preset always uses masking, and the current initialization path is doing extra scalar work that is easy to remove without hurting readability.
outcome: target not reached: 176.963s vs baseline 177.311s (+0.2%, need 5.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.641 | 60.961 |
| 9.449 | 106.753 |
| 9.051 | 100.268 |
| 9.274 | 103.329 |
| 9.341 | 102.965 |
| 8.950 | 102.088 |
| 8.553 | 98.783 |
| 8.800 | 100.792 |
| 9.840 | 111.178 |
| 9.984 | 112.966 |
| 9.693 | 111.110 |
| 9.282 | 105.707 |
| 6.361 | 68.180 |
| 9.604 | 107.748 |
| 9.826 | 108.966 |
| 5.963 | 66.285 |
| 5.947 | 67.056 |
| 6.375 | 68.542 |
| 8.072 | 92.111 |
| 9.389 | 108.029 |
| 7.568 | 84.256 |

# Totals
| user | cpu |
| ---- | ---- |
| 176.963 | 1988.073 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.427 | 94.670 |
