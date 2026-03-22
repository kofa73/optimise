perf: hoist scale parameter computation (ABCD, strength, norm, negligibility) out of the iteration loop

In wavelets_process, the per-scale parameters (equivalent_sigma_at_step, norm via expf, ABCD speeds, strength, and the negligible_scale check) are recomputed identically for every iteration because they depend only on wavelet geometry and user settings, not on pixel data. By precomputing these into small arrays (10 scales max) once before the iteration loop in process() and passing them to wavelets_process, we eliminate N*S redundant calls to the recursive equivalent_sigma_at_step function and N*S expf calls (where N=iterations, S=scales). For presets like denoise with 32 iterations × 10 scales, this saves 320 recursive function calls and 320 expf evaluations. While small relative to per-pixel work, this also enables the compiler to better optimize wavelets_process by reducing its parameter-computation code, and makes the negligible-scale pre-computation (needed for ideas like skipping HF allocation) trivially available.
outcome: target not reached: 191.167s vs baseline 190.343s (-0.4%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.857 | 5.329 |
| 51.239 | 593.225 |
| 4.134 | 42.531 |
| 11.944 | 135.358 |
| 12.014 | 134.620 |
| 17.134 | 197.040 |
| 10.299 | 118.026 |
| 13.674 | 157.759 |
| 10.908 | 122.292 |
| 15.430 | 177.186 |
| 8.620 | 97.693 |
| 4.443 | 48.355 |
| 1.419 | 10.586 |
| 5.987 | 63.807 |
| 13.150 | 148.549 |
| 0.871 | 6.467 |
| 0.716 | 5.143 |
| 1.255 | 9.123 |
| 1.808 | 16.613 |
| 3.243 | 34.144 |
| 2.022 | 18.934 |

# Totals
| user | cpu |
| ---- | ---- |
| 191.167 | 2142.780 |

# Averages
| user | cpu |
| ---- | ---- |
| 9.103 | 102.037 |
