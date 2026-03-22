perf: skip unnecessary MAX(0) negative clamping in bspline blur for diffuse module

Create a diffuse-local bspline decompose wrapper that passes `clip_negatives = FALSE` to `_bspline_vertical_pass` and `_bspline_horizontal`, eliminating the per-pixel per-channel `MAX(0.0f, ...)` operation in both blur passes. This clamping is provably unnecessary for diffuse/sharpen: the PDE solver's output is always non-negative (`fmaxf(result, 0.f)`), so the decomposition input on every iteration is non-negative. Since the B-spline filter weights are all positive (1/16, 4/16, 6/16, 4/16, 1/16), the weighted sum of non-negative inputs is always non-negative, making the MAX dead computation. This removes 2 SIMD MAX instructions per pixel per scale (one vertical, one horizontal), totaling `2 × effective_scales × width × height × iterations` eliminated MAX operations. The savings are most impactful in the horizontal pass where computation (not memory) is the bottleneck.
outcome: target not reached: 176.077s vs baseline 176.483s (+0.2%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.956 | 6.076 |
| 46.931 | 543.836 |
| 3.927 | 40.086 |
| 11.119 | 123.438 |
| 11.054 | 123.640 |
| 15.568 | 177.586 |
| 9.301 | 106.322 |
| 12.349 | 141.592 |
| 9.585 | 106.791 |
| 13.890 | 159.786 |
| 7.857 | 88.572 |
| 4.121 | 44.086 |
| 1.560 | 11.176 |
| 5.665 | 59.538 |
| 12.265 | 137.384 |
| 0.937 | 6.774 |
| 0.755 | 5.094 |
| 1.380 | 9.897 |
| 1.767 | 16.548 |
| 3.059 | 32.012 |
| 2.031 | 18.425 |

# Totals
| user | cpu |
| ---- | ---- |
| 176.077 | 1958.659 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.385 | 93.269 |
