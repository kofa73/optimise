perf: compound memory offsets, inlined accumulation, and skipped expf

Combine three distinct near-miss optimizations (+2-4% individually) into a single, unified loop simplification to drastically reduce register spilling and cross the 5% performance threshold. Specifically, eliminate the `neighbour_pixel_HF` and `neighbour_pixel_LF` matrices by fetching memory via direct offsets directly into the symmetric corner/edge scalar variables, inline the convolution results directly into the `acc` accumulation variable to eliminate the `derivatives` array, and bypass redundant `dt_vector_exp` math for isotropic diffusion orders. Fusing these changes cleanly compounds their individual efficiency gains, resulting in a massive structural reduction in per-pixel array allocations and memory traffic within the innermost loop without altering the bit-exact floating-point evaluation sequence.
outcome: improvement
commit: 0fb78d3ca5
Reduced sum(user) from 247.307s to 231.975s (~6.2% improvement)

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.098 | 8.655 |
| 55.499 | 653.679 |
| 4.393 | 46.711 |
| 14.221 | 161.547 |
| 14.231 | 162.026 |
| 24.476 | 287.111 |
| 16.261 | 190.489 |
| 20.368 | 238.760 |
| 12.231 | 141.703 |
| 18.383 | 214.840 |
| 12.345 | 142.840 |
| 5.254 | 58.681 |
| 1.597 | 13.094 |
| 7.233 | 79.140 |
| 14.113 | 160.803 |
| 0.855 | 6.749 |
| 0.673 | 5.238 |
| 1.406 | 11.467 |
| 1.849 | 18.297 |
| 3.393 | 36.891 |
| 2.096 | 20.431 |

# Totals
| user | cpu |
| ---- | ---- |
| 231.975 | 2659.152 |

# Averages
| user | cpu |
| ---- | ---- |
| 11.046 | 126.626 |
