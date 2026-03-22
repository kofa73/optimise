perf: Factor out quarter-scaling in isotropic accumulation to save inner-loop multiplications

Previous attempts to pre-multiply isotropic constants by `abcd` regressed due to increased register pressure from passing multiple dynamic parameters to the accumulation function. Instead, algebraically rewriting the isotropic kernel accumulation from `abcd * (0.25f * corners + 0.5f * cross - 3.f * center)` to `(abcd * 0.25f) * (corners + 2.f * cross - 12.f * center)` eliminates one floating-point multiplication per channel per order. By passing a single `abcd_quarter` parameter and using hardcoded `2.f` and `12.f` constants (which map perfectly to fast fused-multiply-add instructions), this structurally reduces the ALU cost without register spilling.
outcome: benchmark early abort: Benchmark early abort: 212.434s vs baseline 206.974s (-2.6%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.061 | 6.111 |
| 52.143 | 599.929 |
| 4.132 | 42.910 |
| 12.692 | 138.889 |
| 12.575 | 140.713 |
| 21.321 | 244.121 |
| 14.339 | 161.646 |
| 17.900 | 202.888 |
| 12.380 | 142.628 |
| 16.102 | 181.878 |
| 10.612 | 121.115 |
| 4.871 | 49.106 |
| 1.455 | 10.971 |
| 7.005 | 75.098 |
| 13.807 | 151.797 |
| 0.887 | 6.666 |
| 0.708 | 5.189 |
| 1.312 | 9.590 |
| 1.827 | 17.158 |
| 3.269 | 34.583 |
| 2.036 | 18.928 |

# Totals
| user | cpu |
| ---- | ---- |
| 212.434 | 2361.914 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.116 | 112.472 |
