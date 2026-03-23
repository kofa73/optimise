perf: remove dead code convolution matrix generators

The functions `compute_kernel`, `isotrope_laplacian`, `build_matrix`, `rotation_matrix_gradient`, and `rotation_matrix_isophote` were originally used to populate a 9-element array for generalized kernel convolutions. Since the introduction of `accumulate_convolution_direct`, which computes these symmetries entirely algebraically without intermediate arrays, these generator functions are never called. Removing this 100+ line block of dead code from `diffuse.c` cleans up the file, reduces compilation time, and ensures the compiler does not waste optimization passes analyzing unreachable functions.
outcome: target not reached: 186.947s vs baseline 186.625s (-0.2%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.732 | 61.234 |
| 10.466 | 117.253 |
| 9.052 | 100.198 |
| 10.059 | 110.394 |
| 9.985 | 110.728 |
| 10.341 | 116.849 |
| 9.837 | 113.137 |
| 10.136 | 115.159 |
| 9.884 | 110.955 |
| 10.055 | 112.926 |
| 9.787 | 111.059 |
| 9.338 | 105.520 |
| 6.635 | 70.600 |
| 9.722 | 107.847 |
| 9.919 | 109.077 |
| 6.680 | 74.231 |
| 6.669 | 75.034 |
| 6.669 | 71.033 |
| 8.089 | 91.334 |
| 9.422 | 107.179 |
| 8.470 | 94.300 |

# Totals
| user | cpu |
| ---- | ---- |
| 186.947 | 2086.047 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.902 | 99.336 |
