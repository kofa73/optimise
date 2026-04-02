perf: early-stop coarse-scale CPU iterations when the line drawing update has converged

Add an exact per-scale convergence guard for the CPU path that tracks whether an iteration produced any meaningful change, then stops iterating that scale once further passes would be no-ops within a strict float bound. This targets the large-radius, zero-sharpness, no-mask case where coarse scales can settle before the full iteration budget is exhausted. The win comes from removing entire repeated image sweeps rather than changing the inner math.
outcome: target not reached: instance 12 improved from 6.449s to 6.383s (+1.0%, need 3.0%), overall sum(user) improved from 159.078s to 153.799s (+3.3%); failed gate: target threshold

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.694 | 61.649 |
| 8.153 | 90.308 |
| 7.195 | 78.867 |
| 9.295 | 102.886 |
| 8.422 | 91.817 |
| 8.957 | 101.261 |
| 8.384 | 96.097 |
| 8.717 | 99.572 |
| 0.039 | 0.249 |
| 9.274 | 103.889 |
| 9.239 | 105.262 |
| 8.830 | 99.733 |
| 6.383 | 68.918 |
| 9.055 | 100.702 |
| 8.543 | 93.445 |
| 5.504 | 60.527 |
| 5.523 | 61.437 |
| 6.084 | 65.037 |
| 6.394 | 70.680 |
| 7.393 | 83.085 |
| 6.721 | 74.033 |

# Totals
| user | cpu |
| ---- | ---- |
| 153.799 | 1709.454 |

# Averages
| user | cpu |
| ---- | ---- |
| 7.324 | 81.403 |
