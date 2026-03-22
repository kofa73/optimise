perf: peel bspline horizontal pass to eliminate per-pixel boundary clamping in decomposition

Create a specialized version of `decompose_2D_Bspline` in diffuse.c (or modify bspline.h) that peels the inner horizontal loop of `_bspline_horizontal` into left-edge, center, and right-edge regions — the same proven pattern that yielded ~2.4% from the diffuse column peeling. Currently, `_bspline_horizontal` recomputes 4 MAX/MIN boundary clamps per pixel for the 5-tap B-spline filter indices. For center columns (where `col >= 2*mult` and `col + 2*mult < width`), these clamps are unnecessary. By splitting the horizontal loop into a clamped left edge (0 to 2*mult), an unclamped center (2*mult to width-2*mult) using fixed pointer-offset arithmetic, and a clamped right edge, we eliminate 4 comparisons and 4 conditional-move instructions per pixel from the hot center path. Since `decompose_2D_Bspline` runs once per scale per iteration and processes every pixel, the decomposition accounts for a substantial fraction of total runtime, making this a high-leverage change.
outcome: benchmark early abort: Benchmark early abort: 241.605s vs baseline 206.974s (-16.7%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.091 | 6.700 |
| 60.455 | 579.971 |
| 5.027 | 41.661 |
| 15.001 | 134.371 |
| 14.865 | 135.395 |
| 25.643 | 236.336 |
| 17.021 | 155.332 |
| 21.228 | 195.122 |
| 14.469 | 123.768 |
| 18.022 | 174.343 |
| 10.695 | 114.590 |
| 4.459 | 47.020 |
| 1.437 | 10.836 |
| 6.914 | 73.112 |
| 13.745 | 147.166 |
| 0.949 | 6.327 |
| 0.796 | 5.029 |
| 1.572 | 10.041 |
| 2.082 | 16.845 |
| 3.928 | 32.931 |
| 2.206 | 18.846 |

# Totals
| user | cpu |
| ---- | ---- |
| 241.605 | 2265.742 |

# Averages
| user | cpu |
| ---- | ---- |
| 11.505 | 107.892 |
