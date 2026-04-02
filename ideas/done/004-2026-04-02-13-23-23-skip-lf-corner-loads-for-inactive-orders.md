perf: skip LF corner memory fetches in generic PDE body when 1st/2nd orders are inactive

The generic `diffuse_pixel_body` unconditionally loads all 9 `LF` neighborhood pixels to compute cross and corner sums. However, if the 1st and 2nd order diffusion speeds (`ABCD[0]` and `ABCD[1]`) are exactly zero, the four corner `LF` pixels (`lf0`, `lf2`, `lf6`, `lf8`) and their resulting sums are never utilized in spatial accumulations, because the 3rd and 4th orders only require the axial `LF` pixels to build their gradients. By explicitly checking `ctx->ABCD[0] != 0.f || ctx->ABCD[1] != 0.f` outside the channel loop to conditionally load these corners, we can eliminate 16 memory loads per pixel (4 corners × 4 channels) for 3rd/4th-order-heavy presets that must fall back to the generic loop.
outcome: benchmark early abort: Benchmark early abort: 163.385s vs baseline 158.077s (-3.4%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.783 | 63.077 |
| 8.326 | 93.465 |
| 7.530 | 79.873 |
| 9.643 | 107.917 |
| 9.977 | 107.598 |
| 9.499 | 108.579 |
| 9.034 | 104.893 |
| 9.657 | 107.460 |
| 0.040 | 0.259 |
| 10.295 | 118.173 |
| 10.433 | 116.074 |
| 9.624 | 110.744 |
| 6.046 | 63.528 |
| 9.996 | 111.884 |
| 8.562 | 94.895 |
| 5.793 | 60.486 |
| 5.512 | 61.864 |
| 6.035 | 65.422 |
| 6.673 | 75.572 |
| 8.068 | 88.133 |
| 6.859 | 76.472 |

# Totals
| user | cpu |
| ---- | ---- |
| 163.385 | 1816.368 |

# Averages
| user | cpu |
| ---- | ---- |
| 7.780 | 86.494 |
