perf: Inline derivative accumulation to eliminate intermediate array

Currently, the multi-scale convolution step evaluates four diffusion orders by writing their results to a stack-allocated `derivatives[4]` array (comprising 16 floats). This array is immediately read back in a separate short loop to accumulate the final weighted update into the `acc` variable. By modifying the `compute_convolution_direct` inline function to accept the `ABCD[k]` weight and the `acc` accumulator directly as an `inout` parameter, we can multiply and accumulate the convolution results immediately as they are computed. This refactoring entirely eliminates the stack-allocated intermediate array and its standalone accumulation loop, directly reducing L1 memory traffic and register pressure while strictly preserving the identical mathematical floating-point evaluation order.
outcome: benchmark early abort: Benchmark early abort: 241.559s vs baseline 247.307s (+2.3%, need 5.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.208 | 9.868 |
| 56.100 | 657.749 |
| 4.605 | 49.379 |
| 14.753 | 166.942 |
| 14.742 | 166.231 |
| 25.863 | 300.268 |
| 17.204 | 199.430 |
| 21.523 | 250.028 |
| 12.492 | 137.139 |
| 19.751 | 225.175 |
| 13.110 | 149.854 |
| 5.569 | 61.812 |
| 1.674 | 14.256 |
| 7.555 | 82.499 |
| 14.774 | 168.289 |
| 0.862 | 6.950 |
| 0.697 | 5.361 |
| 1.519 | 12.540 |
| 1.913 | 18.889 |
| 3.496 | 37.867 |
| 2.149 | 21.018 |

# Totals
| user | cpu |
| ---- | ---- |
| 241.559 | 2741.544 |

# Averages
| user | cpu |
| ---- | ---- |
| 11.503 | 130.550 |

outcome: benchmark early abort: Benchmark early abort: 239.269s vs baseline 247.307s (+3.3%, need 5.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.145 | 9.478 |
| 56.366 | 665.560 |
| 4.554 | 48.827 |
| 14.477 | 166.015 |
| 14.513 | 165.799 |
| 25.657 | 300.782 |
| 16.991 | 199.071 |
| 21.294 | 249.927 |
| 12.261 | 141.655 |
| 19.214 | 224.614 |
| 12.912 | 149.695 |
| 5.483 | 61.516 |
| 1.659 | 13.861 |
| 7.465 | 81.974 |
| 14.652 | 167.337 |
| 0.874 | 7.011 |
| 0.689 | 5.515 |
| 1.477 | 12.205 |
| 1.895 | 18.776 |
| 3.527 | 38.300 |
| 2.164 | 21.237 |

# Totals
| user | cpu |
| ---- | ---- |
| 239.269 | 2749.155 |

# Averages
| user | cpu |
| ---- | ---- |
| 11.394 | 130.912 |
