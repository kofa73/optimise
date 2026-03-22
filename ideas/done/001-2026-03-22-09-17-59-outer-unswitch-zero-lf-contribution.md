perf: outer-loop unswitch to skip LF neighbor loads when LF orders have zero speed

When both LF-consuming diffusion orders have zero speed (data->first == 0 && data->second == 0), ABCD[0] and ABCD[1] are zero for every scale, making the LF convolution contribution to `acc` exactly zero. Add an outer-loop unswitched path that skips loading all 8 non-center LF neighbors, skips the LF gradient/angle computation (sqrtf, division), and skips both LF accumulate_convolution_direct calls. Only `LF[index+c]` (the center pixel) is still needed for the final `result = acc + LF[index+c]`. This eliminates 32 float loads per pixel plus all LF gradient and convolution FLOPs. This benefits many common presets including "sharpness|fast", "local contrast|fast", "inpaint highlights", and "watercolor" which all have first=0 and second=0. The optimization follows the proven outer-loop unswitching pattern for simple binary conditions (~6.4% demonstrated improvement).
outcome: benchmark early abort: Benchmark early abort: 235.920s vs baseline 204.349s (-15.4%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.158 | 9.019 |
| 58.134 | 671.775 |
| 3.924 | 40.331 |
| 13.943 | 157.886 |
| 14.051 | 158.703 |
| 24.645 | 282.507 |
| 16.430 | 187.317 |
| 20.576 | 234.947 |
| 10.937 | 125.106 |
| 18.597 | 212.161 |
| 12.642 | 140.457 |
| 5.246 | 58.047 |
| 1.356 | 9.928 |
| 8.069 | 84.403 |
| 15.028 | 171.781 |
| 0.974 | 7.601 |
| 0.768 | 5.918 |
| 1.218 | 8.717 |
| 2.048 | 20.127 |
| 3.895 | 39.374 |
| 2.281 | 22.015 |

# Totals
| user | cpu |
| ---- | ---- |
| 235.920 | 2648.120 |

# Averages
| user | cpu |
| ---- | ---- |
| 11.234 | 126.101 |
