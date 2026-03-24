perf: reduce PDE dispatch macro instantiations from 16 to 9 to shrink icache footprint

The DIFFUSE_PIXEL_BODY macro is currently instantiated 16 times via the 4×4 dispatch of (GRAD_ISOTROPIC, LAPL_ISOTROPIC) × (GRAD_ZERO, LAPL_ZERO). However, when GRAD_ZERO=1, the GRAD_ISOTROPIC parameter has no effect on generated code — all gradient computation (sqrtf, c2, exp, angle math) is dead-code eliminated by the compiler regardless of isotropy. The same applies to LAPL_ZERO=1 and LAPL_ISOTROPIC. By restructuring the dispatch logic to not vary the isotropy parameter when the corresponding direction group has zero speed, we reduce from 4×4=16 to 3×3=9 macro expansions (3 states per group: zero-speed, non-zero-isotropic, non-zero-anisotropic). This reduces the total emitted function body size by roughly 44%, which should reduce instruction cache pressure. The learnings show that excessive code duplication from outer-loop unswitching causes regressions (icache bloat), so reducing unnecessary duplication should help. The code paths taken for the target preset are unchanged — only dead instantiations are eliminated.
outcome: target not reached: 181.596s vs baseline 181.409s (-0.1%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.652 | 61.913 |
| 10.313 | 117.404 |
| 9.028 | 100.295 |
| 9.840 | 110.345 |
| 9.950 | 110.123 |
| 9.497 | 109.118 |
| 9.093 | 105.484 |
| 9.378 | 107.593 |
| 9.754 | 110.244 |
| 9.804 | 111.878 |
| 9.576 | 109.934 |
| 9.103 | 104.044 |
| 6.312 | 68.079 |
| 9.575 | 107.790 |
| 9.838 | 109.449 |
| 6.510 | 73.322 |
| 6.543 | 74.473 |
| 6.352 | 68.669 |
| 7.889 | 90.629 |
| 9.304 | 106.696 |
| 8.285 | 93.689 |

# Totals
| user | cpu |
| ---- | ---- |
| 181.596 | 2051.171 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.647 | 97.675 |
