perf: pre-combine matched LF and HF pixels before computing symmetric spatial sums

When LF and HF convolution speeds are identical (as in "sharpen demosaicing"), the code currently computes symmetric block sums (corners, tb, lr) for LF and HF independently, and then adds the resulting sums together. By pre-adding the raw neighbor pixels immediately after loading (e.g., `px0 = lf0 + hf0`) and computing the symmetric combinations directly from these fused pixels, we avoid computing the structural sums twice. This saves 3 vector additions per channel per pixel and further reduces peak register pressure in the fully-isotropic path.
outcome: target not reached: 173.187s vs baseline 172.940s (-0.1%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.610 | 60.541 |
| 9.062 | 102.328 |
| 8.711 | 96.071 |
| 9.242 | 102.476 |
| 9.232 | 102.388 |
| 8.905 | 101.974 |
| 8.549 | 98.959 |
| 8.778 | 100.071 |
| 9.744 | 110.434 |
| 9.740 | 110.855 |
| 9.441 | 108.435 |
| 9.079 | 103.671 |
| 6.334 | 68.304 |
| 9.286 | 104.424 |
| 9.630 | 106.776 |
| 5.688 | 63.429 |
| 5.733 | 64.449 |
| 6.328 | 68.229 |
| 7.752 | 88.757 |
| 9.093 | 104.716 |
| 7.250 | 80.798 |

# Totals
| user | cpu |
| ---- | ---- |
| 173.187 | 1948.085 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.247 | 92.766 |
