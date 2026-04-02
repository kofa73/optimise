perf: conditionally skip expensive expf evaluation for inactive orders in the generic loop

In the generic `diffuse_pixel_body`, the expensive `dt_vector_exp` function is evaluated for a diffusion order based on its isotropy type and the paired-order macro state (`GRAD_ZERO` or `LAPL_ZERO`). However, if an individual order's speed (e.g., `ABCD[0]`) is exactly zero while its paired order (`ABCD[2]`) is active, the resulting conductance tensor is subsequently multiplied by zero during accumulation, making the `expf` calculation pure dead math. Gating the `dt_vector_exp` calls on `ctx->ABCD[x] != 0.f` reliably prevents this severe exponential math overhead for mixed-order presets without adding complex macro unswitching logic.
outcome: target not reached: instance 13 regressed from 9.691s to 9.797s (-1.1%, need 3.0%), overall sum(user) regressed from 158.077s to 158.718s (-0.4%); failed gate: target threshold

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.704 | 61.850 |
| 8.307 | 93.281 |
| 7.249 | 80.472 |
| 9.370 | 104.175 |
| 9.357 | 104.251 |
| 9.107 | 103.473 |
| 8.702 | 100.798 |
| 8.884 | 102.403 |
| 0.040 | 0.255 |
| 10.088 | 114.501 |
| 9.796 | 112.758 |
| 9.382 | 107.226 |
| 5.949 | 63.171 |
| 9.797 | 109.377 |
| 8.509 | 94.296 |
| 5.531 | 60.773 |
| 5.550 | 62.267 |
| 6.061 | 65.253 |
| 6.683 | 75.819 |
| 7.784 | 88.525 |
| 6.868 | 75.814 |

# Totals
| user | cpu |
| ---- | ---- |
| 158.718 | 1780.738 |

# Averages
| user | cpu |
| ---- | ---- |
| 7.558 | 84.797 |
