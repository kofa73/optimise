perf: bypass edge-conductance math when edge controls are disabled

Route the CPU path through a separate helper when `edge_sensitivity == 0.0f` and `edge_threshold == 0.0f`, and treat the edge conductance as a constant 1.0 instead of rebuilding it per pixel. For the inpaint-highlights instance this condition is fixed for all 33 iterations, so removing the guide-strength normalization, thresholding, and any dependent scalar math should cut a meaningful amount of work from the hottest loop without changing memory traversal.

outcome: benchmark early abort: Benchmark early abort: 176.734s vs baseline 167.053s (-5.8%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.660 | 60.985 |
| 9.522 | 105.629 |
| 10.399 | 118.074 |
| 9.475 | 102.175 |
| 9.227 | 102.654 |
| 9.377 | 103.202 |
| 8.731 | 100.688 |
| 8.924 | 102.555 |
| 0.043 | 0.257 |
| 9.963 | 110.975 |
| 9.514 | 109.115 |
| 9.397 | 103.583 |
| 6.409 | 68.928 |
| 11.565 | 127.152 |
| 11.434 | 128.940 |
| 5.898 | 65.601 |
| 6.214 | 66.386 |
| 6.395 | 69.478 |
| 9.591 | 110.481 |
| 11.516 | 129.718 |
| 7.480 | 83.686 |

# Totals
| user | cpu |
| ---- | ---- |
| 176.734 | 1970.262 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.416 | 93.822 |
