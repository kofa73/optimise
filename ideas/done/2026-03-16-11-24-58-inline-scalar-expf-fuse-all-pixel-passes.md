inline scalar fast-exp to fuse entire pixel body into one channel loop

The per-pixel computation is currently split across 7+ separate for_each_channel passes because dt_vector_exp operates on dt_aligned_pixel_t arrays, forcing a loop boundary between trig/c2 computation and convolution accumulation. This requires ~20 intermediate dt_aligned_pixel_t stack arrays (c2[4], 6 trig, 5 LF sums, 5 HF sums, variance, acc) totaling ~350 bytes — far exceeding x86-64 register capacity and causing heavy spilling. By replacing dt_vector_exp with an inline scalar version of the identical integer-bit-hack fast-exp approximation (same formula, just float instead of dt_aligned_pixel_t), the loop boundary disappears and the entire pixel body — neighbor loading, direction computation, exp, all 4 convolution accumulations, variance regularization, and output — can execute in a single for_each_channel pass where all intermediates are short-lived scalar temporaries consumed immediately after computation. The omp simd pragma still vectorizes across 4 channels since the body has no inter-channel dependencies, and the isotropy_type switches (being channel-invariant) hoist out naturally. This differs from the failed "pair convolutions" experiment (-48.7%) which ADDED convolution work to an existing loop while keeping all arrays; here we ELIMINATE the arrays by pulling convolutions into the loading loop so values are consumed immediately rather than stored and reloaded. Per the learnings, stack array elimination is the dominant optimization lever (all three successful experiments share this theme), and this approach targets all remaining arrays simultaneously, compounding the ~2-4% per-array gains observed in prior individual experiments.

outcome: benchmark early abort: Benchmark early abort: 465.795s vs baseline 217.223s (-114.4%, need 2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.534 | 13.223 |
| 126.973 | 1470.265 |
| 9.323 | 102.047 |
| 29.176 | 332.067 |
| 29.319 | 329.315 |
| 46.059 | 531.369 |
| 30.583 | 353.061 |
| 38.681 | 444.038 |
| 12.334 | 142.549 |
| 34.704 | 397.836 |
| 23.174 | 265.171 |
| 9.709 | 110.252 |
| 3.171 | 27.701 |
| 16.325 | 185.703 |
| 32.860 | 373.162 |
| 1.776 | 17.022 |
| 1.379 | 13.189 |
| 2.567 | 24.316 |
| 3.868 | 41.989 |
| 7.770 | 83.943 |
| 4.510 | 48.057 |

# Totals
| user | cpu |
| ---- | ---- |
| 465.795 | 5306.275 |

# Averages
| user | cpu |
| ---- | ---- |
| 22.181 | 252.680 |
