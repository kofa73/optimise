perf: decompose anisotropic tensor into isotropic base and directional correction

The anisotropic accumulations (isophote and gradient) currently construct and apply explicit `a11` and `a22` tensor components, requiring the computation and storage of both `cos_theta_sq` and `sin_theta_sq` arrays. By algebraically factoring the matrix multiplication (and leveraging `cos2 + sin2 = 1`), the entire anisotropic convolution perfectly decomposes into a scaled Isotropic Laplacian base `0.5 * (1 + c2) * (sum_lr + sum_tb - 4 * center)` plus a Directional Correction term `0.5 * (1 - c2) * [(2 * cos2 - 1) * (sum_lr - sum_tb) - cos_sin * cross_corners]`. This profound mathematical unification completely eliminates the `sin_theta_sq` array requirement, collapses the isophote and gradient paths into identical arithmetic differing only by a `+` or `-` sign on the correction term, and vastly reduces the total arithmetic complexity of the pixel accumulation loop for all anisotropic presets.
outcome: improvement
commit: 74bf9c6715
Reduced sum(user) from 175.941s to 172.940s (~1.7% improvement)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.617 | 60.729 |
| 9.188 | 103.837 |
| 8.741 | 96.518 |
| 9.064 | 101.123 |
| 9.133 | 97.005 |
| 8.866 | 99.105 |
| 8.547 | 92.133 |
| 8.689 | 91.010 |
| 9.756 | 86.731 |
| 9.732 | 109.641 |
| 9.441 | 106.670 |
| 9.048 | 102.685 |
| 6.316 | 66.150 |
| 9.267 | 104.182 |
| 9.606 | 107.066 |
| 5.752 | 63.978 |
| 5.781 | 65.175 |
| 6.295 | 68.255 |
| 7.741 | 88.639 |
| 9.052 | 104.309 |
| 7.308 | 81.479 |

# Totals
| user | cpu |
| ---- | ---- |
| 172.940 | 1896.420 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.235 | 90.306 |
