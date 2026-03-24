perf: eliminate result array in PDE output by computing final value directly into acc

In the DIFFUSE_PIXEL_BODY macro's output section, the code computes `acc[c] = HF * strength + acc[c] / variance[c]` then `result[c] = fmaxf(acc[c] + LF, 0.f)` into a separate dt_aligned_pixel_t result, then nontemporal-stores result. Eliminate the `result` array by computing the final clamped value directly back into `acc[c] = fmaxf(acc[c] + LF[index + c], 0.f)` and passing acc to copy_pixel_nontemporal. This removes one dt_aligned_pixel_t (16 bytes) from the stack in the hottest loop body, reducing register pressure. While small individually, this follows the proven stack-array-elimination pattern and its effect compounds with other register-pressure reductions in the same loop body.
outcome: target not reached: 181.615s vs baseline 181.409s (-0.1%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.658 | 61.169 |
| 10.330 | 117.510 |
| 8.942 | 99.821 |
| 9.939 | 111.538 |
| 9.952 | 111.569 |
| 9.487 | 108.310 |
| 9.127 | 105.797 |
| 9.319 | 107.372 |
| 9.760 | 110.380 |
| 9.800 | 111.809 |
| 9.602 | 110.155 |
| 9.119 | 104.361 |
| 6.395 | 69.248 |
| 9.597 | 108.023 |
| 9.835 | 109.681 |
| 6.496 | 72.917 |
| 6.517 | 74.139 |
| 6.349 | 69.178 |
| 7.900 | 90.341 |
| 9.209 | 106.271 |
| 8.282 | 93.198 |

# Totals
| user | cpu |
| ---- | ---- |
| 181.615 | 2052.787 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.648 | 97.752 |
