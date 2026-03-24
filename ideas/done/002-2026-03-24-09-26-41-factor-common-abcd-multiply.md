perf: factor common ABCD coefficient out of convolution accumulations for equal-speed presets

For the "sharpen demosaicing" preset, all four ABCD values are identical per scale (all speeds = -0.25). Currently, each of the 4 accumulate_convolution_direct calls multiplies its result by its own ABCD[k] value independently. When all four are equal, we can accumulate raw convolution results without the per-convolution ABCD multiply, then multiply the accumulated sum by the common ABCD value once at the end. This saves 3 scalar-vector multiplications per pixel (12 FP operations across 4 channels). The condition (all ABCD equal) is detected at scale level before the pixel loop and dispatched via outer-loop unswitching. Since this eliminates 3 full-width SIMD multiplies rather than just a lightweight check, it follows the successful pattern of outer-loop unswitching for non-trivial per-pixel savings.
outcome: target not reached: 180.971s vs baseline 181.409s (+0.2%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.656 | 61.344 |
| 10.161 | 115.405 |
| 8.936 | 100.577 |
| 9.930 | 110.119 |
| 9.855 | 110.781 |
| 9.480 | 108.632 |
| 9.090 | 105.512 |
| 9.332 | 107.370 |
| 9.761 | 110.663 |
| 9.793 | 111.723 |
| 9.551 | 109.508 |
| 9.079 | 104.314 |
| 6.356 | 67.951 |
| 9.590 | 108.002 |
| 9.833 | 109.485 |
| 6.436 | 72.335 |
| 6.449 | 73.147 |
| 6.321 | 69.023 |
| 7.937 | 90.647 |
| 9.256 | 106.944 |
| 8.169 | 91.867 |

# Totals
| user | cpu |
| ---- | ---- |
| 180.971 | 2045.349 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.618 | 97.398 |
