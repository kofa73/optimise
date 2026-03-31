perf: fold the unit-denominator normalization out of zero-regularization inpaint

Add a narrow CPU fast path for the exact preset shape where `data->regularization == 0.f` and `data->variance_threshold == 0.f`, which makes `regularization_factor` zero and the transformed variance denominator a constant `1`. In that case the solver can skip building the variance accumulator entirely and replace `acc[c] / variance[c]` with a straight add, deleting a full reduction and three divides per active pixel while keeping the generic readable path for every other parameter set.
outcome: benchmark early abort: Benchmark early abort: 188.689s vs baseline 177.311s (-6.4%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.648 | 61.418 |
| 9.762 | 110.451 |
| 9.766 | 106.520 |
| 9.866 | 110.333 |
| 10.202 | 110.446 |
| 9.845 | 112.864 |
| 9.843 | 110.254 |
| 9.671 | 111.595 |
| 9.825 | 112.982 |
| 10.670 | 118.334 |
| 10.093 | 116.105 |
| 9.985 | 110.785 |
| 6.777 | 73.212 |
| 10.375 | 113.201 |
| 10.334 | 115.914 |
| 6.164 | 68.740 |
| 6.464 | 69.080 |
| 6.845 | 74.564 |
| 8.535 | 97.719 |
| 10.225 | 114.166 |
| 7.794 | 87.412 |

# Totals
| user | cpu |
| ---- | ---- |
| 188.689 | 2106.095 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.985 | 100.290 |
