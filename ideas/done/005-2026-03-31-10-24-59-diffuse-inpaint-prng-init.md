perf: remove per-pixel PRNG warmup overhead from inpaint mask seeding

`inpaint_mask` currently rebuilds and warms up RNG state for every masked pixel before producing noise. Replace that with a small deterministic helper that derives the needed state directly from `(row, col)` and emits the Gaussian samples without the repeated splitmix/xoshiro warmup sequence. It only affects the one-time masked initialization pass, so the upside is smaller, but it targets a path this preset always exercises.
outcome: target not reached: 167.037s vs baseline 167.053s (+0.1%, need 3.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.647 | 61.165 |
| 9.364 | 105.386 |
| 8.988 | 101.165 |
| 9.291 | 102.767 |
| 9.217 | 102.653 |
| 9.125 | 103.937 |
| 8.738 | 101.085 |
| 8.949 | 102.975 |
| 0.039 | 0.245 |
| 9.842 | 111.067 |
| 9.511 | 109.089 |
| 9.139 | 103.809 |
| 6.363 | 68.314 |
| 9.713 | 108.479 |
| 9.946 | 110.498 |
| 5.898 | 65.657 |
| 5.925 | 66.193 |
| 6.396 | 69.196 |
| 8.048 | 92.070 |
| 9.428 | 107.813 |
| 7.470 | 83.621 |

# Totals
| user | cpu |
| ---- | ---- |
| 167.037 | 1877.184 |

# Averages
| user | cpu |
| ---- | ---- |
| 7.954 | 89.390 |
