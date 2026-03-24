perf: sum matched gradient and laplacian tensors to halve convolution multiplications

For passes where both gradient and laplacian orders are matched (such as the target "sharpen demosaicing / AA filter" preset), the pixel loop currently calls `accumulate_convolution_direct` twice, sequentially applying the gradient and laplacian tensor weights to the same `LF + HF` symmetric pixel combinations. By decoupling the tensor component evaluation from the spatial neighbor accumulation, we can algebraically sum the scaled gradient and laplacian tensors (`ABCD[0] * tensor_grad + ABCD[1] * tensor_lapl`) into a single combined tensor before applying it. This halves the number of heavy inner-loop array multiplications against the neighbor pixels and reduces register pressure by consuming the spatial arrays immediately.
outcome: benchmark early abort: Benchmark early abort: 185.144s vs baseline 172.940s (-7.1%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.827 | 61.635 |
| 9.875 | 104.702 |
| 9.400 | 96.519 |
| 9.995 | 101.009 |
| 9.864 | 100.418 |
| 9.671 | 101.785 |
| 9.357 | 98.685 |
| 9.425 | 100.968 |
| 10.348 | 107.477 |
| 10.327 | 110.057 |
| 10.369 | 108.051 |
| 9.837 | 102.669 |
| 6.842 | 67.695 |
| 10.027 | 104.338 |
| 9.980 | 107.273 |
| 6.094 | 65.588 |
| 6.428 | 66.264 |
| 6.607 | 69.053 |
| 7.900 | 88.588 |
| 9.466 | 103.879 |
| 7.505 | 82.973 |

# Totals
| user | cpu |
| ---- | ---- |
| 185.144 | 1949.626 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.816 | 92.839 |
