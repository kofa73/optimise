perf: Skip dt_vector_exp calls for isotropic diffusion orders where c2 is unused

In `heat_PDE_diffusion`, `dt_vector_exp` is called unconditionally 4 times per pixel to compute the anisotropy damping factor `c2[k]` for each diffusion order. However, when `isotropy_type[k] == DT_ISOTROPY_ISOTROPE` (user anisotropy parameter is zero), the isotrope path in `compute_convolution_direct` uses fixed kernel weights and never reads `c2[k]`, making that exp() call pure waste. Since `isotropy_type` is determined once from module parameters before the pixel loop, guarding each `dt_vector_exp` call with `if(isotropy_type[k] != DT_ISOTROPY_ISOTROPE)` produces perfectly-predicted branches at effectively zero cost. Most real-world presets have at least 2 of 4 orders set to isotropic (e.g. lens deblur, denoise, and dehaze all have `anisotropy_second=0` and `anisotropy_fourth=0`), saving 2 expensive vectorized transcendental function calls per pixel—roughly 50% of the total exp cost. Unlike the failed "skip zero speed orders" optimization which changed floating-point accumulation by omitting `derivatives[k] * ABCD[k]` terms (where 0×NaN ≠ 0), this change only avoids computing a value that is provably never consumed by the downstream switch case, leaving all convolutions, accumulations, and output values bit-identical.
outcome: benchmark early abort: Benchmark early abort: 242.658s vs baseline 247.307s (+1.9%, need 5.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.181 | 9.406 |
| 57.406 | 670.145 |
| 4.622 | 49.008 |
| 14.940 | 169.231 |
| 15.118 | 168.638 |
| 25.580 | 297.446 |
| 16.952 | 197.592 |
| 21.341 | 247.531 |
| 12.320 | 140.345 |
| 19.336 | 222.437 |
| 12.876 | 148.408 |
| 5.491 | 61.089 |
| 1.668 | 14.317 |
| 7.734 | 83.270 |
| 15.227 | 171.410 |
| 0.899 | 7.159 |
| 0.719 | 5.508 |
| 1.486 | 12.346 |
| 1.986 | 18.992 |
| 3.541 | 38.526 |
| 2.235 | 21.234 |

# Totals
| user | cpu |
| ---- | ---- |
| 242.658 | 2754.038 |

# Averages
| user | cpu |
| ---- | ---- |
| 11.555 | 131.145 |

outcome: benchmark early abort: Benchmark early abort: 239.358s vs baseline 247.307s (+3.2%, need 5.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.152 | 9.557 |
| 55.759 | 657.918 |
| 4.595 | 49.285 |
| 14.617 | 166.689 |
| 14.624 | 167.289 |
| 25.682 | 301.540 |
| 17.135 | 200.632 |
| 21.352 | 250.307 |
| 12.243 | 142.074 |
| 19.272 | 225.410 |
| 12.976 | 149.861 |
| 5.496 | 61.486 |
| 1.688 | 14.196 |
| 7.497 | 82.310 |
| 14.725 | 168.304 |
| 0.870 | 6.960 |
| 0.677 | 5.348 |
| 1.498 | 12.582 |
| 1.869 | 18.646 |
| 3.485 | 37.741 |
| 2.146 | 20.966 |

# Totals
| user | cpu |
| ---- | ---- |
| 239.358 | 2749.101 |

# Averages
| user | cpu |
| ---- | ---- |
| 11.398 | 130.910 |
