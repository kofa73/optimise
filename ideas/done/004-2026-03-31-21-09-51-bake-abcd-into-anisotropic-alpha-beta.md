perf: bake ABCD speed factors into anisotropic alpha/beta coefficients to save inner-loop multiplications

In `accumulate_convolution_direct` and `accumulate_isophote_convolution_direct`, the anisotropic accumulations apply the ABCD speed factor at the very end of the formula: `acc += abcd * (alpha * iso_base +- beta * dir_corr)`. Since `abcd` is loop-invariant and `alpha`/`beta` are computed locally as `0.5f * (1.0f +- c2[c])`, we can pre-multiply the `0.5f` by `abcd` outside the accumulation logic to form `half_abcd`, and bake it directly into `alpha = half_abcd * (1.0f + c2[c])` and `beta = half_abcd * (1.0f - c2[c])`. This seamlessly eliminates the final `abcd * (...)` multiplication from the deepest part of the anisotropic FMA chain without altering the underlying tensor summation structure.
outcome: target not reached: 163.476s vs baseline 163.578s (-1.2%, need 3.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.681 | 61.056 |
| 9.545 | 105.677 |
| 9.011 | 101.229 |
| 9.372 | 102.823 |
| 9.309 | 103.395 |
| 8.995 | 102.202 |
| 8.579 | 98.908 |
| 8.797 | 100.866 |
| 0.038 | 0.250 |
| 9.802 | 110.767 |
| 9.476 | 108.484 |
| 9.093 | 102.815 |
| 6.413 | 68.606 |
| 9.651 | 108.132 |
| 10.002 | 110.715 |
| 5.419 | 59.499 |
| 5.412 | 60.324 |
| 6.399 | 68.721 |
| 7.223 | 81.756 |
| 8.413 | 96.024 |
| 6.846 | 75.564 |

# Totals
| user | cpu |
| ---- | ---- |
| 163.476 | 1827.813 |

# Averages
| user | cpu |
| ---- | ---- |
| 7.785 | 87.039 |
