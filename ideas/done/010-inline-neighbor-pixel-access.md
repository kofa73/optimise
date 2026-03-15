eliminate stack-allocated neighbor arrays via direct memory fetches

The inner loop currently gathers non-local pixels into 9-element `neighbour_pixel_HF` and `neighbour_pixel_LF` local arrays prior to calculation. These large upfront allocations (72 floats per pixel) cause heavy register spilling and stack memory traffic. Instead of doing a bulk block copy, we can fetch the specific pixels directly from the `HF` and `LF` pointers inline at the exact moments they are needed for the gradient stencils, variance accumulation, and symmetric convolutions. Relying on the L1 cache to handle these redundant localized reads is significantly faster than thrashing the stack with large intermediate arrays.
outcome: benchmark early abort: obvious regression

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.281 | 9.196 |
| 55.825 | 636.392 |
| 4.594 | 47.121 |
| 14.273 | 156.824 |
| 14.434 | 158.406 |
| 25.679 | 290.094 |
| 17.072 | 192.850 |
| 21.200 | 240.511 |
| 12.670 | 140.571 |
| 19.249 | 217.226 |
| 12.962 | 144.150 |
| 5.538 | 59.375 |
| 1.717 | 13.121 |
| 7.421 | 77.687 |
| 14.449 | 158.792 |
| 0.977 | 7.368 |
| 0.790 | 5.850 |
| 1.551 | 11.560 |
| 1.943 | 18.515 |
| 3.540 | 36.681 |
| 2.244 | 20.419 |

# Totals
| user | cpu |
| ---- | ---- |
| 239.409 | 2642.709 |

# Averages
| user | cpu |
| ---- | ---- |
| 11.400 | 125.843 |

outcome: benchmark early abort: Benchmark early abort: 237.410s vs baseline 247.307s (+4.0%, need 5.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.176 | 9.256 |
| 55.691 | 654.906 |
| 4.559 | 48.501 |
| 14.170 | 160.682 |
| 14.157 | 161.511 |
| 25.552 | 298.408 |
| 17.135 | 198.942 |
| 21.302 | 248.405 |
| 12.280 | 142.272 |
| 19.171 | 222.815 |
| 12.932 | 148.698 |
| 5.506 | 61.175 |
| 1.614 | 13.331 |
| 7.249 | 79.156 |
| 14.247 | 162.032 |
| 0.874 | 6.972 |
| 0.701 | 5.410 |
| 1.475 | 11.795 |
| 1.933 | 19.062 |
| 3.502 | 37.574 |
| 2.184 | 21.023 |

# Totals
| user | cpu |
| ---- | ---- |
| 237.410 | 2711.926 |

# Averages
| user | cpu |
| ---- | ---- |
| 11.305 | 129.139 |
