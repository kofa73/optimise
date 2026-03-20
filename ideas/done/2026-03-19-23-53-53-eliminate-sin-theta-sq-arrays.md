perf: eliminate sin_theta_sq arrays by rewriting anisotropic tensors via 1 - cos2

The anisotropic tensor weights currently require both `cos_theta2` and `sin_theta2` stack arrays. Because `sin²(θ) = 1 - cos²(θ)`, we can algebraically rewrite the isophote weights as `a11 = c2 + cos_theta2 * (1 - c2)` and `a22 = 1.0f - cos_theta2 * (1 - c2)`. This mathematically identical formulation allows us to completely remove the `sin_theta_grad_sq` and `sin_theta_lapl_sq` arrays from the stack, saving L1 memory traffic and the ALU instructions used to compute `sqf(sin_grad)`.
outcome: benchmark early abort: Benchmark early abort: 222.091s vs baseline 217.223s (-2.2%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.913 | 6.164 |
| 55.858 | 647.068 |
| 4.466 | 47.075 |
| 13.173 | 144.329 |
| 13.289 | 145.631 |
| 22.138 | 253.114 |
| 14.477 | 167.837 |
| 18.516 | 210.365 |
| 12.594 | 137.961 |
| 16.413 | 189.930 |
| 11.363 | 125.689 |
| 4.750 | 51.775 |
| 1.519 | 11.904 |
| 7.483 | 79.574 |
| 14.256 | 161.263 |
| 0.929 | 7.211 |
| 0.751 | 5.606 |
| 1.346 | 10.236 |
| 1.948 | 18.968 |
| 3.748 | 36.523 |
| 2.161 | 20.499 |

# Totals
| user | cpu |
| ---- | ---- |
| 222.091 | 2478.722 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.576 | 118.034 |
