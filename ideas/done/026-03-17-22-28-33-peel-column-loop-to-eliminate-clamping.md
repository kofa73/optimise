perf: peel column loop boundaries to eliminate max/min clamping from PDE convolution

The hot `DIFFUSE_ROW_LOOP` in `heat_PDE_diffusion` computes spatial boundary clamps (`MAX(j - mult, 0)` and `MIN(j + mult, width - 1)`) for every pixel `j`. Since the clamp offsets are invariant for the majority of the image row, peeling the column loop into three discrete sections (left edge, center, right edge) allows the innermost center loop to safely omit the `MAX`/`MIN` logic entirely. Extracting the main loop body into an inline function and executing it across these peeled sections enables the compiler to use fixed scalar arithmetic for memory offsets relative to `j`, reducing data dependencies and eliminating bounds-checking instructions without adding branch divergence inside the core processing region.
outcome: target not reached

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.898 | 6.091 |
| 55.737 | 647.887 |
| 4.444 | 46.157 |
| 12.595 | 141.734 |
| 12.604 | 141.278 |
| 21.819 | 250.327 |
| 14.276 | 165.681 |
| 17.933 | 207.045 |
| 12.534 | 140.511 |
| 16.234 | 186.950 |
| 10.860 | 124.251 |
| 4.664 | 50.458 |
| 1.464 | 11.264 |
| 7.204 | 78.005 |
| 14.092 | 159.481 |
| 0.906 | 6.915 |
| 0.729 | 5.182 |
| 1.299 | 9.647 |
| 1.946 | 17.965 |
| 3.466 | 36.857 |
| 2.170 | 20.382 |

# Totals
| user | cpu |
| ---- | ---- |
| 217.874 | 2454.068 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.375 | 116.860 |
