Compute cos²θ, sin²θ, and cosθ·sinθ directly from squared gradient magnitude (gx²/m², gy²/m², gx·gy/m²) instead of normalizing the gradient first then squaring.

Reuses gx² and gy² already computed for magnitude, eliminating redundant squarings and one division per gradient direction per channel.

outcome: benchmark early abort: Benchmark early abort: 212.424s vs baseline 217.223s (+2.2%, need 3.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.013 | 6.418 |
| 53.985 | 629.376 |
| 4.269 | 44.978 |
| 12.549 | 141.923 |
| 12.569 | 141.910 |
| 20.985 | 244.767 |
| 13.957 | 162.180 |
| 17.591 | 203.626 |
| 12.279 | 140.928 |
| 15.758 | 183.006 |
| 10.626 | 121.718 |
| 4.536 | 49.905 |
| 1.438 | 11.375 |
| 7.053 | 76.739 |
| 13.780 | 156.295 |
| 0.851 | 6.636 |
| 0.668 | 5.059 |
| 1.289 | 9.825 |
| 1.839 | 18.152 |
| 3.318 | 35.915 |
| 2.071 | 19.933 |

# Totals
| user | cpu |
| ---- | ---- |
| 212.424 | 2410.664 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.115 | 114.794 |
