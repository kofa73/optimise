perf: outer-loop unswitch for zero sharpness to eliminate per-pixel strength multiply

When data->sharpness == 0 (the default and the case for 14 of 19 presets), strength is always exactly 1.0f for every scale (since strength = sharpness * norm + 1.0f). The per-pixel computation `HF[index+c] * strength` in the final integration degenerates to `HF[index+c]`, saving 4 multiplies per pixel per channel. Add an outer-loop unswitching check on `data->sharpness == 0.0f` that selects a pixel body variant where the strength multiply is eliminated. This follows the proven pattern of outer-loop unswitching for simple binary conditions with per-pixel savings, and the condition is evaluated once per heat_PDE_diffusion call (not per pixel), keeping the branch overhead negligible.
outcome: benchmark early abort: Benchmark early abort: 226.644s vs baseline 200.347s (-13.1%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.258 | 9.732 |
| 58.495 | 676.046 |
| 4.689 | 49.894 |
| 14.764 | 166.838 |
| 13.312 | 150.372 |
| 21.990 | 251.294 |
| 14.393 | 162.611 |
| 18.065 | 206.472 |
| 10.922 | 125.350 |
| 17.340 | 197.211 |
| 10.962 | 125.328 |
| 5.244 | 53.700 |
| 1.537 | 12.019 |
| 7.235 | 79.301 |
| 15.337 | 171.649 |
| 0.960 | 7.617 |
| 0.783 | 6.011 |
| 1.344 | 10.383 |
| 2.041 | 20.032 |
| 3.688 | 39.660 |
| 2.285 | 22.060 |

# Totals
| user | cpu |
| ---- | ---- |
| 226.644 | 2543.580 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.793 | 121.123 |
