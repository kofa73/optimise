perf: Unswitch row bounds to provide compiler with static memory offsets between rows

Currently, the `i_neighbours` array is computed using `MAX` and `MIN` to clamp row boundaries. This dynamic clamping prevents the compiler from proving that the three memory rows are separated by a constant stride, forcing it to maintain three independent base pointers. By unswitching the vertical `i` bounds check (`i >= step && i < height - step`) outside the peeled column loop, we can use exact algebraic offsets (`i - step`, `i`, `i + step`) for the safe center rows. This enables the compiler to optimize the inner loop's memory fetches using constant-offset scaled addressing.
outcome: benchmark early abort: Benchmark early abort: 262.141s vs baseline 206.974s (-26.7%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.237 | 9.537 |
| 63.385 | 731.658 |
| 5.048 | 53.969 |
| 15.718 | 175.306 |
| 15.476 | 176.314 |
| 27.771 | 315.479 |
| 18.124 | 211.324 |
| 23.067 | 265.174 |
| 12.551 | 140.354 |
| 20.647 | 236.152 |
| 14.018 | 157.615 |
| 5.907 | 65.411 |
| 1.780 | 14.889 |
| 8.394 | 91.996 |
| 16.612 | 185.890 |
| 1.034 | 8.433 |
| 0.819 | 6.588 |
| 1.597 | 13.121 |
| 2.196 | 21.768 |
| 4.290 | 42.894 |
| 2.470 | 24.026 |

# Totals
| user | cpu |
| ---- | ---- |
| 262.141 | 2947.898 |

# Averages
| user | cpu |
| ---- | ---- |
| 12.483 | 140.376 |
