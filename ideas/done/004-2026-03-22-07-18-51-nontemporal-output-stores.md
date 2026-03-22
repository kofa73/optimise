perf: use streaming stores for output writes to reduce cache pollution

Replace the output write `out[index + c] = fmaxf(...)` in DIFFUSE_PIXEL_BODY with nontemporal (streaming) stores using `copy_pixel_nontemporal` or equivalent intrinsics. Each output pixel is written exactly once per scale, and the output buffer is not read again until the next scale's `heat_PDE_diffusion` call, by which point the entire image (~300MB for a 20MP image) has been traversed and the written data has been naturally evicted from cache. Using nontemporal stores avoids the write-allocate cache protocol (which reads a cache line from memory, modifies it, then writes it back), preventing eviction of useful LF/HF input data from L1/L2 cache. This follows the same pattern already used in `decompose_2D_Bspline` via the `USE_NONTEMPORAL` mechanism. The benefit is greatest for large images where the working set far exceeds cache capacity; a size-based heuristic could conditionally enable this optimization.
outcome: improvement
commit: c3f0e46ef3
Reduced sum(user) from 206.974s to 204.349s (~1.3% improvement)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.850 | 5.306 |
| 51.153 | 592.962 |
| 4.097 | 42.706 |
| 12.017 | 134.271 |
| 11.982 | 135.288 |
| 20.676 | 237.098 |
| 13.789 | 157.479 |
| 17.061 | 197.192 |
| 10.932 | 122.341 |
| 15.556 | 177.129 |
| 10.371 | 117.543 |
| 4.466 | 48.455 |
| 1.418 | 10.584 |
| 6.831 | 72.693 |
| 13.195 | 148.563 |
| 0.876 | 6.641 |
| 0.728 | 5.209 |
| 1.256 | 9.177 |
| 1.822 | 17.024 |
| 3.250 | 33.960 |
| 2.023 | 18.922 |

# Totals
| user | cpu |
| ---- | ---- |
| 204.349 | 2290.543 |

# Averages
| user | cpu |
| ---- | ---- |
| 9.731 | 109.073 |
