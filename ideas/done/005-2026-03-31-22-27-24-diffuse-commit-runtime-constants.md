perf: precompute immutable diffuse runtime constants in committed params

`wavelets_process()` recomputes `anisotropy[]`, `isotropy_type[]`, `regularization`, and `variance_threshold` every outer iteration even though they depend only on module parameters. Extend `dt_iop_diffuse_data_t` with a compact runtime block filled once in `commit_params()` and consume that from `process()`/`wavelets_process()`. The direct savings are modest, but it also makes the CPU helper dispatch cleaner and cheaper, which is useful if more targeted fast paths are added for common presets.
outcome: target not reached: 164.035s vs baseline 163.578s (-0.9%, need 3.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.678 | 60.985 |
| 9.478 | 105.389 |
| 9.001 | 101.296 |
| 9.299 | 102.459 |
| 9.263 | 102.718 |
| 9.116 | 103.982 |
| 8.746 | 100.844 |
| 8.936 | 102.608 |
| 0.040 | 0.238 |
| 9.879 | 111.227 |
| 9.536 | 109.351 |
| 9.157 | 103.961 |
| 6.401 | 68.630 |
| 9.736 | 108.788 |
| 9.974 | 110.248 |
| 5.419 | 59.710 |
| 5.424 | 60.616 |
| 6.429 | 68.967 |
| 7.230 | 81.962 |
| 8.402 | 96.219 |
| 6.891 | 75.730 |

# Totals
| user | cpu |
| ---- | ---- |
| 164.035 | 1835.928 |

# Averages
| user | cpu |
| ---- | ---- |
| 7.811 | 87.425 |
