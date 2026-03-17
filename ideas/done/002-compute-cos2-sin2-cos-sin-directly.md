Compute cos²θ, sin²θ, and cosθ·sinθ directly from squared gradient magnitude (gx²/m², gy²/m², gx·gy/m²) instead of normalizing the gradient first then squaring.

Reuses gx² and gy² already computed for magnitude, eliminating redundant squarings and one division per gradient direction per channel.

outcome: benchmark early abort: Benchmark early abort: 216.304s vs baseline 217.223s (+0.4%, need 2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.910 | 6.088 |
| 54.526 | 628.236 |
| 4.281 | 44.890 |
| 12.984 | 142.240 |
| 12.702 | 143.341 |
| 21.429 | 245.457 |
| 14.331 | 162.224 |
| 18.078 | 203.807 |
| 12.359 | 141.446 |
| 16.175 | 182.723 |
| 10.687 | 122.007 |
| 4.846 | 49.913 |
| 1.486 | 11.463 |
| 7.109 | 77.034 |
| 14.116 | 156.609 |
| 0.895 | 6.975 |
| 0.726 | 5.380 |
| 1.320 | 9.842 |
| 1.882 | 18.236 |
| 3.367 | 36.302 |
| 2.095 | 19.882 |

# Totals
| user | cpu |
| ---- | ---- |
| 216.304 | 2414.095 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.300 | 114.957 |
