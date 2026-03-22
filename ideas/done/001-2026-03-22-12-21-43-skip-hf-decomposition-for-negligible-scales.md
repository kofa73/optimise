perf: skip HF buffer allocation and subtraction writes during decomposition for negligible wavelet scales

Pre-compute which wavelet scales will have negligible Gaussian norm weight (using equivalent_sigma_at_step and the norm formula) before the decomposition loop begins. For those scales, skip allocating HF[s] entirely and pass a NULL HF pointer to decompose_2D_Bspline (or use a lightweight variant that only computes the blur output without the `HF[index] = in[index] - blur` subtraction and nontemporal write). This extends the existing negligible-scale PDE skip (which only avoids reconstruction work) upstream to also eliminate one full write pass per negligible scale during decomposition. For a 24MP image, each skipped HF write saves ~384MB of memory bandwidth. This follows the proven function-level guard pattern (~2% from skip-pde-negligible-norm) and reduces peak memory allocation.
outcome: improvement
commit: 36bd2c5178
Reduced sum(user) from 200.347s to 190.343s (~5.0% improvement)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.848 | 5.286 |
| 50.898 | 590.895 |
| 4.109 | 42.076 |
| 11.968 | 134.423 |
| 12.049 | 134.326 |
| 17.068 | 197.541 |
| 10.231 | 117.899 |
| 13.600 | 156.531 |
| 10.906 | 122.042 |
| 15.395 | 176.638 |
| 8.600 | 96.849 |
| 4.423 | 47.623 |
| 1.417 | 10.519 |
| 5.977 | 63.145 |
| 13.027 | 147.758 |
| 0.854 | 5.969 |
| 0.691 | 4.937 |
| 1.248 | 9.164 |
| 1.812 | 16.773 |
| 3.211 | 33.896 |
| 2.011 | 18.843 |

# Totals
| user | cpu |
| ---- | ---- |
| 190.343 | 2133.133 |

# Averages
| user | cpu |
| ---- | ---- |
| 9.064 | 101.578 |
