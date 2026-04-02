perf: keep the coarsest HF scales in short-lived scratch instead of long-lived HF buffers

Treat the top one or two coarsest HF scales as short-lived data: store them in scratch that is consumed immediately when reconstruction begins, while only finer scales remain in the long-lived `HF[]` array. This targets the worst-reuse-distance buffers in the local-contrast preset, cutting heap-backed full-frame traffic and pressure on cache/TLBs without changing traversal order or touching the OpenCL path.
outcome: target not reached: instance 2 regressed from 9.018s to 9.067s (-0.5%, need 3.0%), overall sum(user) regressed from 163.012s to 163.491s (-0.3%); failed gate: target threshold

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.682 | 61.667 |
| 9.540 | 106.038 |
| 9.067 | 102.265 |
| 9.316 | 102.914 |
| 9.250 | 103.153 |
| 9.146 | 104.458 |
| 8.733 | 101.094 |
| 8.957 | 103.151 |
| 0.040 | 0.252 |
| 9.876 | 111.736 |
| 9.539 | 109.707 |
| 9.196 | 104.466 |
| 6.425 | 69.277 |
| 9.690 | 109.177 |
| 9.176 | 101.417 |
| 5.426 | 60.029 |
| 5.449 | 61.154 |
| 6.448 | 69.699 |
| 7.225 | 82.517 |
| 8.442 | 96.637 |
| 6.868 | 76.329 |

# Totals
| user | cpu |
| ---- | ---- |
| 163.491 | 1837.137 |

# Averages
| user | cpu |
| ---- | ---- |
| 7.785 | 87.483 |
