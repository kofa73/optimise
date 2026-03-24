perf: fuse matched gradient and laplacian accumulations for fully isotropic presets

The fully-isotropic fast path currently processes matched gradient (orders 1 and 3) and matched laplacian (orders 2 and 4) diffusions as two distinct spatial convolutions. For presets like "sharpen demosaicing" where all four orders share identical speeds (`first = second = third = fourth = -0.25f`), `ABCD[0]` is equal to `ABCD[1]`. By introducing an `ALL_MATCHED` macro path, we can algebraically combine the gradient and laplacian speed coefficients into a single `(ABCD[0] + ABCD[1])` scalar and compute the entire isotropic PDE accumulation in a single step. This halves the convolution arithmetic and stencil combinations compared to the existing paired-matched path.
outcome: target not reached: 176.156s vs baseline 175.941s (-0.1%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.628 | 60.738 |
| 9.494 | 106.262 |
| 8.938 | 100.679 |
| 9.271 | 102.866 |
| 9.266 | 103.308 |
| 9.069 | 103.057 |
| 8.693 | 100.676 |
| 8.881 | 102.381 |
| 9.746 | 110.150 |
| 9.807 | 111.980 |
| 9.582 | 109.892 |
| 9.093 | 104.326 |
| 6.344 | 68.491 |
| 9.627 | 107.159 |
| 9.846 | 109.945 |
| 5.911 | 65.816 |
| 5.925 | 67.041 |
| 6.333 | 68.438 |
| 7.951 | 90.932 |
| 9.275 | 106.711 |
| 7.476 | 83.972 |

# Totals
| user | cpu |
| ---- | ---- |
| 176.156 | 1984.820 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.388 | 94.515 |
