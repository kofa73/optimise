perf: pre-combine LF+HF stencil sums for matched gradient and laplacian order pairs

For the "sharpen demosaicing" preset, gradient orders 0 and 2 share the same c2, theta, and isotropy_type (both ISOPHOTE with anisotropy=1.0). Their convolutions use the same kernel but different input data (LF vs HF). Since ABCD[0]==ABCD[2], the two accumulations ABCD[0]*conv(LF,K) + ABCD[2]*conv(HF,K) = ABCD[0]*conv(LF+HF,K). By pre-computing combined stencil sums (combined_cross = LF_cross + HF_cross, combined_sum_corners = LF_sum_corners + HF_sum_corners, etc.) and evaluating one convolution on the combined data with coefficient ABCD[0]+ABCD[2], we halve the convolution evaluation count from 4 to 2. Each ISOPHOTE convolution evaluation involves ~8 FP ops per channel, so eliminating 2 evaluations saves ~64 FP operations per pixel. The 5 per-channel additions to combine sums cost only ~20 ops, yielding a net savings of ~44 ops per pixel. The condition is detected at scale level (matching isotropy_type and anisotropy for the pair), dispatched via the same outer-loop unswitching infrastructure.
outcome: improvement
commit: eb30fd0544
Reduced sum(user) from 181.409s to 175.941s (~3.0% improvement)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.612 | 60.857 |
| 9.421 | 106.689 |
| 9.020 | 100.419 |
| 9.229 | 103.001 |
| 9.234 | 102.905 |
| 9.071 | 103.262 |
| 8.672 | 100.427 |
| 8.905 | 102.159 |
| 9.761 | 110.457 |
| 9.784 | 111.610 |
| 9.544 | 109.133 |
| 9.053 | 103.964 |
| 6.347 | 68.236 |
| 9.558 | 107.735 |
| 9.833 | 109.607 |
| 5.890 | 65.902 |
| 5.934 | 67.125 |
| 6.329 | 68.811 |
| 7.962 | 90.438 |
| 9.261 | 107.011 |
| 7.521 | 84.165 |

# Totals
| user | cpu |
| ---- | ---- |
| 175.941 | 1983.913 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.378 | 94.472 |
