perf: dynamically prune fourth-order tensor math inside the third-fourth CPU helper

Following the relaxation of the `third_fourth_isophote` CPU helper to support third-order-only presets, the helper will natively execute redundant math for the inactive fourth order (calculating HF laplacians, magnitude, and expensive `dt_vector_exp` scalings). By explicitly gating the `c2_lapl` tensor generation, `expf` scaling, and laplacian accumulation on `ctx->ABCD[3] != 0.f` within the helper's pixel body, we ensure the helper provides maximum throughput for both true third/fourth mixed presets and pure third-order-only instances. This perfectly-predicted branch halves the ALU workload for third-order-only presets without requiring the code duplication of a separate helper instance.
outcome: target not reached: instance 13 improved from 9.691s to 9.651s (+0.4%, need 3.0%), overall sum(user) regressed from 158.077s to 158.233s (-0.1%); failed gate: target threshold

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.711 | 61.812 |
| 8.359 | 93.038 |
| 8.103 | 90.532 |
| 9.329 | 103.571 |
| 9.338 | 103.018 |
| 9.140 | 104.643 |
| 8.827 | 101.607 |
| 9.035 | 103.442 |
| 0.040 | 0.256 |
| 9.863 | 111.804 |
| 9.591 | 110.044 |
| 9.161 | 105.032 |
| 5.463 | 57.498 |
| 9.651 | 108.558 |
| 8.564 | 94.093 |
| 5.566 | 60.923 |
| 5.559 | 62.154 |
| 5.542 | 59.225 |
| 6.723 | 75.218 |
| 7.780 | 88.820 |
| 6.888 | 76.433 |

# Totals
| user | cpu |
| ---- | ---- |
| 158.233 | 1771.721 |

# Averages
| user | cpu |
| ---- | ---- |
| 7.535 | 84.368 |
