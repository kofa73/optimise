perf: skip unnecessary MAX(0) negative clamping in bspline blur for diffuse module

Create a diffuse-local bspline decompose wrapper that passes `clip_negatives = FALSE` to `_bspline_vertical_pass` and `_bspline_horizontal`, eliminating the per-pixel per-channel `MAX(0.0f, ...)` operation in both blur passes. This clamping is provably unnecessary for diffuse/sharpen: the PDE solver's output is always non-negative (`fmaxf(result, 0.f)`), so the decomposition input on every iteration is non-negative. Since the B-spline filter weights are all positive (1/16, 4/16, 6/16, 4/16, 1/16), the weighted sum of non-negative inputs is always non-negative, making the MAX dead computation. This removes 2 SIMD MAX instructions per pixel per scale (one vertical, one horizontal), totaling `2 × effective_scales × width × height × iterations` eliminated MAX operations. The savings are most impactful in the horizontal pass where computation (not memory) is the bottleneck.

outcome: target not reached: 187.727s vs baseline 188.886s (+0.6%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.839 | 62.587 |
| 10.656 | 118.476 |
| 9.123 | 101.195 |
| 10.098 | 111.254 |
| 9.985 | 110.865 |
| 10.330 | 116.015 |
| 9.878 | 113.181 |
| 10.095 | 115.815 |
| 9.904 | 110.621 |
| 10.000 | 112.750 |
| 9.722 | 110.423 |
| 9.305 | 104.820 |
| 6.701 | 71.193 |
| 9.738 | 108.084 |
| 9.951 | 109.645 |
| 6.731 | 74.799 |
| 6.727 | 75.745 |
| 6.738 | 72.029 |
| 8.143 | 92.430 |
| 9.530 | 108.325 |
| 8.533 | 95.063 |

# Totals
| user | cpu |
| ---- | ---- |
| 187.727 | 2095.315 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.939 | 99.777 |
