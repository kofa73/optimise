perf: hoist matched combined pixel arrays to shared pixel body scope

When both gradient and laplacian passes are matched (e.g., in uniform-speed presets), the `DIFFUSE_PIXEL_BODY` macro redundantly declares and computes symmetric combinations like `combined_sum_corners` inside isolated lexical blocks for both the `GRAD` and `LAPL` evaluation phases. While compilers attempt Common Subexpression Elimination, these physically duplicated stack array declarations artificially spike peak register pressure and risk triggering stack spills before the intermediate representation is fully optimized. Hoisting a single, shared set of `combined_*` arrays to the top of the pixel body loop guarantees they are allocated and computed exactly once, tightening the stack frame and facilitating pristine register allocation.
outcome: target not reached: 172.974s vs baseline 172.940s (-0.0%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.624 | 61.068 |
| 9.121 | 102.936 |
| 8.731 | 96.994 |
| 9.094 | 101.450 |
| 9.130 | 101.019 |
| 8.947 | 102.294 |
| 8.564 | 99.161 |
| 8.805 | 101.092 |
| 9.755 | 110.514 |
| 9.715 | 110.742 |
| 9.409 | 108.239 |
| 9.047 | 102.809 |
| 6.334 | 68.099 |
| 9.310 | 104.483 |
| 9.597 | 106.462 |
| 5.711 | 63.665 |
| 5.745 | 64.806 |
| 6.307 | 68.180 |
| 7.732 | 88.469 |
| 9.005 | 103.944 |
| 7.291 | 81.375 |

# Totals
| user | cpu |
| ---- | ---- |
| 172.974 | 1947.801 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.237 | 92.752 |
