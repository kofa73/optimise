perf: apply cross-pixel OpenMP SIMD vectorization to fully isotropic peeled loops

Currently, vectorization in the hot pixel paths relies purely on compiler auto-vectorization across the 4 color channels within a single pixel (`for_each_channel`), which caps SIMD utilization at 128 bits. The peeled center column loops (`center_start` to `center_end`) have no boundary checks, no loop-carried dependencies, and for fully isotropic presets (like the AA filter), no non-vectorizable exponential function calls. By applying a `#pragma omp simd` directive directly to this inner `j` loop when `GRAD_ISOTROPIC` and `LAPL_ISOTROPIC` are true, we compel the compiler to vectorize operations across multiple pixels concurrently, unlocking 256-bit or 512-bit registers (AVX2/AVX-512) and drastically multiplying computational throughput.
outcome: target not reached: 173.069s vs baseline 172.940s (-0.1%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.614 | 60.820 |
| 9.272 | 103.240 |
| 8.638 | 97.192 |
| 9.131 | 101.024 |
| 9.116 | 101.634 |
| 8.895 | 101.541 |
| 8.565 | 98.744 |
| 8.731 | 100.464 |
| 9.743 | 110.357 |
| 9.652 | 110.504 |
| 9.437 | 108.508 |
| 9.044 | 103.255 |
| 6.330 | 68.042 |
| 9.370 | 103.896 |
| 9.583 | 107.432 |
| 5.736 | 63.911 |
| 5.781 | 64.862 |
| 6.291 | 68.524 |
| 7.750 | 88.642 |
| 9.084 | 103.984 |
| 7.306 | 81.848 |

# Totals
| user | cpu |
| ---- | ---- |
| 173.069 | 1948.424 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.241 | 92.782 |
