perf: drop unused low-order runtime state on third-fourth-order-only presets

Introduce a compact runtime descriptor for presets where first- and second-order speeds are exactly zero, and thread that through the CPU path so no low-order coefficient arrays, per-scale bookkeeping, or reconstruction-side integration state are prepared or touched. This goes beyond merely skipping inner-loop arithmetic: it trims whole-scale setup and buffer traffic that still exists for inactive orders in the generic path. The change should stay maintainable if expressed as a small dedicated descriptor/helper rather than more macro or branch layering.
outcome: target not reached: instance 14 regressed from 9.154s to 9.164s (-0.1%, need 3.0%), overall sum(user) improved from 161.306s to 161.119s (+0.1%); failed gate: target threshold

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.699 | 61.654 |
| 9.492 | 106.322 |
| 7.250 | 80.492 |
| 9.309 | 102.789 |
| 9.254 | 103.231 |
| 9.047 | 103.627 |
| 8.749 | 101.272 |
| 8.935 | 102.939 |
| 0.039 | 0.247 |
| 9.857 | 111.392 |
| 9.529 | 109.472 |
| 9.150 | 104.192 |
| 6.301 | 67.832 |
| 9.628 | 108.403 |
| 9.164 | 101.225 |
| 5.397 | 59.785 |
| 5.398 | 60.746 |
| 6.418 | 70.024 |
| 7.237 | 81.747 |
| 8.393 | 96.624 |
| 6.873 | 76.193 |

# Totals
| user | cpu |
| ---- | ---- |
| 161.119 | 1810.208 |

# Averages
| user | cpu |
| ---- | ---- |
| 7.672 | 86.200 |
