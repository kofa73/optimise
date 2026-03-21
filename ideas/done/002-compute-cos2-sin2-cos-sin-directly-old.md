Compute cos²θ, sin²θ, and cosθ·sinθ directly from squared gradient magnitude (gx²/m², gy²/m², gx·gy/m²) instead of normalizing the gradient first then squaring.

Reuses gx² and gy² already computed for magnitude, eliminating redundant squarings and one division per gradient direction per channel.

outcome: target not reached

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.886 | 6.049 |
| 54.058 | 629.288 |
| 4.271 | 44.545 |
| 12.610 | 142.698 |
| 12.763 | 142.056 |
| 21.235 | 245.336 |
| 13.958 | 162.919 |
| 17.801 | 203.813 |
| 12.327 | 137.897 |
| 15.825 | 184.166 |
| 10.811 | 121.734 |
| 4.559 | 50.106 |
| 1.465 | 11.367 |
| 7.080 | 76.319 |
| 13.846 | 156.534 |
| 0.879 | 6.749 |
| 0.708 | 5.233 |
| 1.287 | 9.851 |
| 1.863 | 18.035 |
| 3.340 | 35.412 |
| 2.070 | 19.411 |

# Totals
| user | cpu |
| ---- | ---- |
| 213.642 | 2409.518 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.173 | 114.739 |
