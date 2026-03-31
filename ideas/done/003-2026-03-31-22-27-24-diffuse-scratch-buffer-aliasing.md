perf: collapse diffuse full-frame scratch buffers through lifetime-based aliasing

`process()` keeps four full-resolution float buffers live at once (`temp1`, `temp2`, `LF_odd`, `LF_even`) on top of the HF pyramid. Add a small scratch-layout planner so the outer-iteration ping-pong buffer that is dead during `wavelets_process()` aliases one LF scratch role, reducing peak memory by one full image without changing traversal order or arithmetic. On the max-scale local-contrast preset, shrinking the working set should lower TLB/cache pressure more than another small ALU tweak.
outcome: target not reached: 163.000s vs baseline 163.578s (-0.3%, need 3.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.596 | 60.962 |
| 9.397 | 105.820 |
| 9.106 | 101.151 |
| 9.222 | 102.899 |
| 9.267 | 102.297 |
| 9.008 | 103.295 |
| 8.705 | 100.221 |
| 8.887 | 102.476 |
| 0.039 | 0.247 |
| 9.692 | 110.830 |
| 9.562 | 108.818 |
| 9.098 | 104.148 |
| 6.378 | 67.937 |
| 9.614 | 108.230 |
| 9.911 | 110.523 |
| 5.377 | 59.582 |
| 5.384 | 60.491 |
| 6.352 | 68.983 |
| 7.201 | 81.340 |
| 8.376 | 96.168 |
| 6.828 | 75.825 |

# Totals
| user | cpu |
| ---- | ---- |
| 163.000 | 1832.243 |

# Averages
| user | cpu |
| ---- | ---- |
| 7.762 | 87.250 |
