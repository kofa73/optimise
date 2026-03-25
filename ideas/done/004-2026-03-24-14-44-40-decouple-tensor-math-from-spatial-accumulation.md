perf: decouple tensor evaluation from spatial convolution to prevent duplicate math

For unmatched gradient or laplacian passes (where LF and HF scales operate at different speeds), the `accumulate_convolution_direct` inline function is called twice—once for the LF neighbor array and once for the HF array—passing the exact same local anisotropic variables both times. Because the tensor setup (evaluating trigonometric components) is tightly coupled inside the accumulation function, the compiler is forced to duplicate this math or rely on unreliable CSE. By explicitly decoupling the tensor component evaluation from the spatial multiplication step, we ensure the tensor factors are computed exactly once per order and then cleanly applied to both the LF and HF spatial arrays independently, structurally guaranteeing no duplicated math.
outcome: benchmark early abort: Benchmark early abort: 181.908s vs baseline 172.940s (-5.2%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.670 | 62.106 |
| 9.712 | 106.029 |
| 8.942 | 100.985 |
| 9.854 | 106.792 |
| 9.514 | 106.531 |
| 9.345 | 107.361 |
| 9.356 | 104.623 |
| 9.191 | 106.121 |
| 10.016 | 110.678 |
| 10.171 | 116.744 |
| 10.255 | 113.998 |
| 9.439 | 108.704 |
| 6.496 | 70.462 |
| 10.009 | 108.725 |
| 9.906 | 111.318 |
| 5.925 | 66.097 |
| 6.167 | 67.005 |
| 6.521 | 71.203 |
| 8.084 | 92.798 |
| 9.810 | 109.442 |
| 7.525 | 84.438 |

# Totals
| user | cpu |
| ---- | ---- |
| 181.908 | 2032.160 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.662 | 96.770 |
