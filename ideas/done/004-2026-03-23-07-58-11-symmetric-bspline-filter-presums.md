perf: exploit B-spline filter symmetry to reduce critical-path latency in decomposition blur

The sparse_scalar_product function used in both vertical and horizontal B-spline blur passes computes a 5-tap convolution with symmetric coefficients [1,4,6,4,1]/16 as a chain of 5 FMA operations (5-deep dependency chain). By pre-summing symmetric input pairs (buf[-2]+buf[+2] and buf[-1]+buf[+1]) before multiplying by the shared coefficient, the computation becomes 2 independent additions followed by a 3-deep FMA chain, reducing the critical-path latency from 5 to ~4 cycles. Create a local specialized version of the horizontal and vertical blur for the diffuse decomposition that uses this symmetric formulation. While the total operation count is similar, the shorter dependency chain allows better instruction-level parallelism and pipeline utilization, which matters because the blur passes run for every pixel × every scale × both passes × every iteration.
outcome: target not reached: 181.514s vs baseline 181.409s (-0.1%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.635 | 61.612 |
| 10.282 | 116.984 |
| 9.032 | 100.551 |
| 9.855 | 110.555 |
| 9.917 | 110.437 |
| 9.436 | 108.323 |
| 9.094 | 105.508 |
| 9.344 | 107.554 |
| 9.752 | 110.020 |
| 9.770 | 111.393 |
| 9.528 | 109.093 |
| 9.107 | 103.911 |
| 6.349 | 68.614 |
| 9.586 | 107.774 |
| 9.830 | 109.522 |
| 6.511 | 73.473 |
| 6.560 | 74.634 |
| 6.354 | 68.674 |
| 7.941 | 90.928 |
| 9.289 | 107.216 |
| 8.342 | 93.662 |

# Totals
| user | cpu |
| ---- | ---- |
| 181.514 | 2050.438 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.644 | 97.640 |
