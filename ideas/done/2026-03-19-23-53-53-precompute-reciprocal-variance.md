perf: precompute reciprocal variance to replace division in final integration loop

Floating-point division is a high-latency operation that severely bottlenecks the final state update loop (`acc[c] / variance[c]`). By precomputing the reciprocal directly during the preceding regularization pass (`variance[c] = 1.0f / (variance_threshold + variance[c] * regularization_factor)`), we can convert the division in the integration loop into a much faster multiplication (`acc[c] * variance[c]`). This shifts the latency outside of the highly congested accumulator loop.
outcome: benchmark early abort: Benchmark early abort: 224.003s vs baseline 217.223s (-3.1%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.892 | 6.028 |
| 57.840 | 666.878 |
| 4.527 | 47.938 |
| 13.237 | 144.991 |
| 13.007 | 146.150 |
| 22.112 | 252.979 |
| 14.704 | 166.723 |
| 18.355 | 209.318 |
| 12.337 | 142.353 |
| 16.654 | 188.715 |
| 11.247 | 124.776 |
| 4.726 | 51.595 |
| 1.510 | 11.814 |
| 7.426 | 81.230 |
| 14.785 | 164.162 |
| 0.918 | 7.155 |
| 0.732 | 5.645 |
| 1.363 | 10.246 |
| 1.955 | 19.137 |
| 3.517 | 37.749 |
| 2.159 | 20.844 |

# Totals
| user | cpu |
| ---- | ---- |
| 224.003 | 2506.426 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.667 | 119.354 |
