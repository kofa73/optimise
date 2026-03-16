Compute cos²θ, sin²θ, and cosθ·sinθ directly from squared gradient magnitude (gx²/m², gy²/m², gx·gy/m²) instead of normalizing the gradient first then squaring.

Reuses gx² and gy² already computed for magnitude, eliminating redundant squarings and one division per gradient direction per channel.

outcome: benchmark early abort: Benchmark early abort: 223.923s vs baseline 231.975s (+3.5%, need 5.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.063 | 8.314 |
| 54.132 | 629.929 |
| 4.343 | 45.096 |
| 13.721 | 154.149 |
| 13.556 | 154.072 |
| 23.246 | 272.337 |
| 15.539 | 180.906 |
| 19.423 | 227.035 |
| 12.231 | 141.230 |
| 17.511 | 204.058 |
| 11.761 | 135.659 |
| 5.019 | 55.793 |
| 1.531 | 12.371 |
| 7.028 | 76.636 |
| 13.743 | 156.413 |
| 0.849 | 6.763 |
| 0.677 | 5.164 |
| 1.364 | 10.848 |
| 1.821 | 18.064 |
| 3.308 | 36.007 |
| 2.057 | 19.859 |

# Totals
| user | cpu |
| ---- | ---- |
| 223.923 | 2550.703 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.663 | 121.462 |
