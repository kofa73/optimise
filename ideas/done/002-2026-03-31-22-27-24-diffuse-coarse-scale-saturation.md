perf: specialize fully clamped coarse diffuse scales

When `mult` becomes large relative to the ROI, the dilated 3x3 stencil in `heat_PDE_diffusion()` collapses onto a much smaller set of distinct border samples, but the generic code still gathers full neighborhoods and builds full kernels. Detect scales where `mult` has saturated one or both image dimensions and route them to an exact degenerate helper, or stop at the last non-degenerate level and fold the remaining work into a cheaper terminal pass. This should particularly help the large-radius local-contrast preset, which spends a disproportionate amount of time in the coarsest scales.
outcome: benchmark early abort: Benchmark early abort: 183.572s vs baseline 163.578s (-12.2%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 6.895 | 73.454 |
| 9.456 | 106.697 |
| 9.228 | 100.191 |
| 10.775 | 121.284 |
| 11.176 | 121.819 |
| 11.002 | 126.637 |
| 10.865 | 122.235 |
| 10.810 | 125.363 |
| 0.040 | 0.244 |
| 11.972 | 134.005 |
| 11.388 | 131.293 |
| 11.154 | 124.681 |
| 7.479 | 81.710 |
| 9.713 | 109.101 |
| 10.096 | 110.839 |
| 5.444 | 60.196 |
| 5.437 | 60.816 |
| 7.903 | 83.206 |
| 7.251 | 82.166 |
| 8.556 | 96.162 |
| 6.932 | 76.132 |

# Totals
| user | cpu |
| ---- | ---- |
| 183.572 | 2048.231 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.742 | 97.535 |
