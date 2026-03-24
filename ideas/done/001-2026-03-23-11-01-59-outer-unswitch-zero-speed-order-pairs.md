perf: outer-loop unswitch to skip paired zero-speed gradient/laplacian order groups

Pre-compute two boolean flags outside the pixel loop: `grad_orders_zero = (ABCD[0] == 0 && ABCD[2] == 0)` and `lapl_orders_zero = (ABCD[1] == 0 && ABCD[3] == 0)`. Use these as compile-time macro parameters in the DIFFUSE_PIXEL_BODY to generate specialized code paths. When a pair is zero, skip the entire paired computation: the shared angle computation (gradient angles from LF or laplacian angles from HF), both dt_vector_exp calls for that pair, and both convolution accumulations. Many common presets (all denoise variants) set second=0 and fourth=0, making the laplacian pair zero and allowing ~36% of per-pixel ALU to be skipped. This differs from per-pixel zero-speed checks (which the learnings show fail) because it is a compile-time outer-loop unswitch with no inner-loop branches, matching the proven +6.4% pattern.
outcome: improvement
commit: bede39b0b2
Reduced sum(user) from 186.625s to 181.409s (~2.8% improvement)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.674 | 61.174 |
| 10.432 | 118.136 |
| 8.964 | 100.989 |
| 9.936 | 110.759 |
| 9.880 | 110.467 |
| 9.505 | 108.697 |
| 9.151 | 105.488 |
| 9.333 | 106.949 |
| 9.748 | 110.112 |
| 9.831 | 111.548 |
| 9.516 | 109.387 |
| 9.088 | 103.867 |
| 6.344 | 67.835 |
| 9.603 | 107.111 |
| 9.810 | 109.637 |
| 6.471 | 72.628 |
| 6.504 | 73.923 |
| 6.338 | 68.892 |
| 7.870 | 89.875 |
| 9.213 | 105.303 |
| 8.198 | 92.594 |

# Totals
| user | cpu |
| ---- | ---- |
| 181.409 | 2045.371 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.639 | 97.399 |
