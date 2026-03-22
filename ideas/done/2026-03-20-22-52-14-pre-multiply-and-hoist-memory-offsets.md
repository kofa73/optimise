perf: Pre-multiply and hoist row/column memory offsets to reduce inner-loop ALU

Extract the multiplication by 4 out of the 9 neighbor index calculations in the innermost pixel loops. Pre-multiply the `i_neighbours` array by 4 outside the column loop, and multiply the `j_neighbours` by 4 once inside the loop. Then calculate `n0` through `n8` using simple scalar additions. This replaces 9 independent integer index multiplications per pixel with pre-computed offset additions, reducing ALU instruction pressure in the address generation logic.
outcome: target not reached: 207.491s vs baseline 206.974s (-0.2%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.907 | 6.029 |
| 51.668 | 593.122 |
| 4.155 | 42.787 |
| 12.347 | 137.783 |
| 12.429 | 137.940 |
| 20.774 | 236.878 |
| 13.623 | 156.503 |
| 17.079 | 197.024 |
| 12.395 | 138.833 |
| 15.428 | 176.367 |
| 10.418 | 117.403 |
| 4.456 | 47.796 |
| 1.444 | 10.791 |
| 6.960 | 73.641 |
| 13.506 | 151.250 |
| 0.878 | 5.925 |
| 0.691 | 5.008 |
| 1.280 | 9.400 |
| 1.796 | 16.445 |
| 3.241 | 33.781 |
| 2.016 | 18.841 |

# Totals
| user | cpu |
| ---- | ---- |
| 207.491 | 2313.547 |

# Averages
| user | cpu |
| ---- | ---- |
| 9.881 | 110.169 |
