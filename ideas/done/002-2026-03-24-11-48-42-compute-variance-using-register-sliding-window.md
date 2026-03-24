perf: compute 3x3 variance using a register-based sliding window

The high-frequency variance calculation performs 9 floating-point multiplications and 8 additions per channel for every pixel independently. By exploiting the separable nature of the 3x3 unweighted sum-of-squares window, we can compute vertical column squares (`S(j) = hf_top^2 + hf_center^2 + hf_bottom^2`) and maintain them in three local SIMD variables (`left`, `center`, `right`). As the column loop advances, we shift these registers and only calculate the single new rightmost column. This sliding window approach slashes the ALU cost from 9 squares to 3, and 8 additions to 4 per pixel, entirely within native registers without any cache-blocking or memory overhead.
outcome: target not reached: 174.917s vs baseline 175.941s (+0.6%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.615 | 60.968 |
| 9.436 | 105.564 |
| 8.815 | 99.372 |
| 9.295 | 102.874 |
| 9.228 | 102.999 |
| 8.993 | 102.504 |
| 8.638 | 99.856 |
| 8.857 | 101.893 |
| 9.766 | 110.086 |
| 9.710 | 111.129 |
| 9.547 | 108.717 |
| 8.996 | 103.281 |
| 6.359 | 68.381 |
| 9.570 | 106.583 |
| 9.681 | 108.508 |
| 5.816 | 65.054 |
| 5.889 | 66.188 |
| 6.306 | 68.782 |
| 7.809 | 89.494 |
| 9.176 | 105.081 |
| 7.415 | 83.298 |

# Totals
| user | cpu |
| ---- | ---- |
| 174.917 | 1970.612 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.329 | 93.839 |
