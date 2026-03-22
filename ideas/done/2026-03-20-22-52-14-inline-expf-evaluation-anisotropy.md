perf: Inline expf evaluation for anisotropy tensors to eliminate loops

Move the `expf` calculation for the `c2` tensors directly into the first channel loop where `magnitude_grad` and `magnitude_lapl` are computed, rather than storing intermediate negated values and running a separate `dt_vector_exp` iteration later. Since the `c2` values are conditionally evaluated based on isotropy, conditionally applying `expf(-magnitude * anisotropy)` inline eliminates 4 small secondary vector loops and avoids transient intermediate array stack writes.
outcome: benchmark early abort: Benchmark early abort: 560.606s vs baseline 206.974s (-170.9%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.920 | 6.141 |
| 156.449 | 1816.381 |
| 12.869 | 142.506 |
| 32.855 | 377.352 |
| 33.088 | 376.693 |
| 55.182 | 643.123 |
| 37.030 | 426.649 |
| 46.009 | 534.342 |
| 12.529 | 140.628 |
| 41.089 | 478.749 |
| 27.991 | 319.239 |
| 11.541 | 132.206 |
| 3.479 | 34.933 |
| 20.854 | 236.426 |
| 41.356 | 475.141 |
| 2.191 | 21.918 |
| 1.737 | 17.312 |
| 3.325 | 30.089 |
| 4.911 | 54.081 |
| 9.539 | 108.447 |
| 5.662 | 62.005 |

# Totals
| user | cpu |
| ---- | ---- |
| 560.606 | 6434.361 |

# Averages
| user | cpu |
| ---- | ---- |
| 26.696 | 306.398 |
