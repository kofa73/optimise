perf: combine paired ABCD coefficients to halve convolution calls on fully-isotropic path

In the fully-isotropic unswitched path (DIFFUSE_ROW_LOOP(1,1)), all four accumulate_convolution_direct calls use the isotropic kernel formula: `acc += abcd * (0.25*corners + 0.5*(tb+lr) - 3*center)`. Since orders 0 and 1 both operate on LF data with the same isotropic kernel, their contributions are `ABCD[0]*iso(LF) + ABCD[1]*iso(LF) = (ABCD[0]+ABCD[1])*iso(LF)`. Similarly for HF: `(ABCD[2]+ABCD[3])*iso(HF)`. Pre-compute `ABCD_LF = ABCD[0]+ABCD[1]` and `ABCD_HF = ABCD[2]+ABCD[3]` as loop-invariant constants, then replace 4 convolution calls with 2. This saves ~56 FLOPs per pixel on the isotropic path. Unlike prior attempts to pair ALL convolution calls (which caused -48.7% regression from register pressure in anisotropic paths), this targets only the isotropic path where the algebra is trivially correct and no extra state is needed.
outcome: target not reached: 200.500s vs baseline 200.347s (-0.1%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.830 | 5.177 |
| 51.059 | 592.154 |
| 4.102 | 42.401 |
| 11.979 | 134.653 |
| 12.033 | 134.812 |
| 19.828 | 228.304 |
| 12.932 | 148.855 |
| 16.284 | 187.983 |
| 10.904 | 122.123 |
| 15.352 | 176.854 |
| 9.964 | 112.906 |
| 4.421 | 47.904 |
| 1.411 | 10.539 |
| 6.376 | 68.171 |
| 13.117 | 147.723 |
| 0.872 | 6.558 |
| 0.720 | 5.242 |
| 1.250 | 9.092 |
| 1.807 | 17.334 |
| 3.236 | 33.944 |
| 2.023 | 18.914 |

# Totals
| user | cpu |
| ---- | ---- |
| 200.500 | 2251.643 |

# Averages
| user | cpu |
| ---- | ---- |
| 9.548 | 107.221 |
