perf: Outer-loop unswitch matched LF/HF anisotropy to safely skip dt_vector_exp

While attempting to skip redundant `dt_vector_exp` calls for matched LF/HF anisotropy *inside* the pixel loop caused a catastrophic regression due to branching dependencies, evaluating this match as an outer-loop condition (`anisotropy[0] == anisotropy[2]`) allows us to safely bypass up to two expensive vector `expf` computations per pixel without SIMD breakage. Since the default presets frequently use identical anisotropies for low and high frequencies, unswitching this path offers a massive reduction in ALU load for the most common use cases.
outcome: benchmark early abort: Benchmark early abort: 242.332s vs baseline 206.974s (-17.1%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.004 | 6.934 |
| 56.885 | 661.201 |
| 5.111 | 52.462 |
| 14.507 | 162.870 |
| 14.695 | 161.871 |
| 25.040 | 287.528 |
| 16.933 | 191.968 |
| 21.104 | 241.411 |
| 12.371 | 142.626 |
| 18.932 | 215.353 |
| 12.836 | 143.529 |
| 5.394 | 59.325 |
| 1.710 | 13.761 |
| 8.113 | 88.911 |
| 16.304 | 180.913 |
| 0.978 | 7.552 |
| 0.776 | 5.837 |
| 1.517 | 11.993 |
| 1.983 | 19.420 |
| 3.901 | 38.053 |
| 2.238 | 21.441 |

# Totals
| user | cpu |
| ---- | ---- |
| 242.332 | 2714.959 |

# Averages
| user | cpu |
| ---- | ---- |
| 11.540 | 129.284 |
