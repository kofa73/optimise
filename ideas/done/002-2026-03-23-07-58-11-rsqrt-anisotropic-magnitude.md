perf: replace sqrtf with fast reciprocal-sqrt path for anisotropic gradient magnitude

In the anisotropic gradient/laplacian sections of the PDE pixel body, replace `magnitude = sqrtf(mag_sq)` followed by `c2 = -magnitude * half_anisotropy` with `c2 = -mag_sq * rsqrtf(mag_sq) * half_anisotropy`, using a platform-appropriate fast reciprocal square root (e.g., _mm_rsqrt_ps on x86, vrsqrte on ARM). The rsqrt path executes in ~5-6 cycles vs ~12-14 cycles for full-precision sqrt, saving ~6-8 cycles per call. There are 2 sqrtf calls per anisotropic pixel (gradient + laplacian), so this saves ~12-16 cycles per pixel. The ~12-bit precision of hardware rsqrt is acceptable because the result feeds into dt_vector_exp which is itself a low-precision integer-trick approximation. Handle the zero-magnitude case with a conditional or by adding a tiny epsilon to mag_sq before rsqrt.
outcome: target not reached: 188.102s vs baseline 186.625s (-0.8%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.743 | 61.221 |
| 10.572 | 118.919 |
| 9.258 | 101.613 |
| 10.025 | 111.255 |
| 10.096 | 110.996 |
| 10.254 | 115.195 |
| 9.891 | 104.039 |
| 10.091 | 105.942 |
| 9.877 | 96.088 |
| 9.969 | 112.477 |
| 9.710 | 110.740 |
| 9.318 | 105.108 |
| 6.608 | 70.612 |
| 9.893 | 109.284 |
| 10.072 | 111.965 |
| 6.790 | 75.692 |
| 6.807 | 75.922 |
| 6.677 | 71.568 |
| 8.239 | 93.389 |
| 9.598 | 109.058 |
| 8.614 | 95.894 |

# Totals
| user | cpu |
| ---- | ---- |
| 188.102 | 2066.977 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.957 | 98.427 |
