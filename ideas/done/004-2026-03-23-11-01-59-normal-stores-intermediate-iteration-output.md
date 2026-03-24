perf: use temporal stores for scale-0 PDE output during non-final iterations

The PDE solver currently uses `copy_pixel_nontemporal` for all output writes, bypassing cache. However, for non-final iterations (it < iterations-1), the scale-0 reconstruction output becomes the very next decomposition's input. Both scale-0 reconstruction and scale-0 decomposition process rows linearly (mult=1, so `dwt_interleave_rows` returns identity order). Using normal (temporal) stores for this intermediate output keeps recently-written rows in L2/L3 cache, so the next iteration's decomposition reads hit cache instead of fetching from RAM. Add a `use_nontemporal` parameter to `heat_PDE_diffusion` (or use a separate store path for `s == 0 && !is_final_iteration`). The learnings show nontemporal stores for buffers read soon after cause -68.8% regression, confirming the value of temporal stores when data is reused immediately.
outcome: target not reached: 182.040s vs baseline 181.409s (-0.3%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.719 | 62.271 |
| 10.269 | 116.808 |
| 8.903 | 100.046 |
| 9.960 | 110.542 |
| 9.870 | 110.848 |
| 9.546 | 109.025 |
| 9.194 | 106.811 |
| 9.426 | 107.797 |
| 10.096 | 114.291 |
| 9.807 | 111.864 |
| 9.549 | 109.709 |
| 9.103 | 104.250 |
| 6.386 | 68.766 |
| 9.588 | 107.953 |
| 9.860 | 109.831 |
| 6.479 | 73.061 |
| 6.523 | 74.142 |
| 6.364 | 69.117 |
| 7.895 | 90.168 |
| 9.219 | 106.283 |
| 8.284 | 92.813 |

# Totals
| user | cpu |
| ---- | ---- |
| 182.040 | 2056.396 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.669 | 97.924 |
