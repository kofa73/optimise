perf: split heat_PDE_diffusion into unclamped interior and border kernels

Peel `heat_PDE_diffusion()` in both dimensions, not just by column, so the large center rectangle runs through a helper with no `MAX/MIN` clamping and no per-pixel boundary coordinate setup. The strong instance is full-frame, unmasked, and iterated many times, so most pixels live in that interior region; removing both x and y clamp work there should cut hot-loop ALU and give the compiler a cleaner vectorizable kernel.
outcome: benchmark early abort: Benchmark early abort: 177.342s vs baseline 167.053s (-6.2%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.894 | 60.612 |
| 9.543 | 107.619 |
| 10.675 | 117.480 |
| 9.307 | 103.617 |
| 9.284 | 103.457 |
| 9.305 | 102.635 |
| 8.618 | 99.598 |
| 9.199 | 101.939 |
| 0.040 | 0.254 |
| 9.721 | 110.991 |
| 9.779 | 108.399 |
| 9.063 | 103.595 |
| 6.410 | 69.187 |
| 11.555 | 127.073 |
| 11.422 | 129.136 |
| 6.265 | 66.349 |
| 5.974 | 67.289 |
| 6.425 | 69.834 |
| 9.981 | 111.387 |
| 11.326 | 131.435 |
| 7.556 | 84.643 |

# Totals
| user | cpu |
| ---- | ---- |
| 177.342 | 1976.529 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.445 | 94.120 |
