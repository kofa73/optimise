phase gradient/laplacian angle processing into scoped blocks to reduce peak register pressure

Restructure the inner pixel body of heat_PDE_diffusion so that gradient-dependent orders (0,2) and laplacian-dependent orders (1,3) are processed in separate scoped blocks. The main for_each_channel loop fetches all 18 neighbors and computes only the 10 combination arrays (LF/HF cross, corners, tb, lr, center) plus variance — but no angles or c2 values. Then a scoped block for gradient orders re-reads 4 directional LF neighbors from L1 cache, computes gradient angle (cos²θ, sin²θ, cosθsinθ) and c2[0]/c2[2] locally, applies dt_vector_exp, and calls accumulate_convolution_direct for orders 0 and 2. A second scoped block does the same for laplacian orders using 4 HF neighbors. Because the gradient-angle arrays (3) and gradient-c2 arrays (2) go out of scope before the laplacian block begins, the compiler can reuse their stack slots. This reduces peak simultaneously-live dt_aligned_pixel_t arrays from 22 to 17 — cutting register spills from ~6 to ~1 on SSE — at the cost of only 32 extra float reads per pixel from data already in L1 cache. This follows the proven dominant optimization pattern in this code: reducing intermediate stack arrays in the innermost loop to alleviate register spilling.

outcome: benchmark early abort: Benchmark early abort: 226.016s vs baseline 217.223s (-4.0%, need 2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.900 | 5.978 |
| 58.371 | 679.416 |
| 4.804 | 47.407 |
| 13.009 | 147.043 |
| 13.318 | 146.428 |
| 22.211 | 255.827 |
| 14.765 | 169.271 |
| 18.307 | 213.629 |
| 12.539 | 137.903 |
| 16.778 | 191.139 |
| 11.075 | 127.245 |
| 4.766 | 52.392 |
| 1.531 | 11.834 |
| 7.769 | 80.802 |
| 14.714 | 166.767 |
| 0.975 | 7.699 |
| 0.858 | 5.715 |
| 1.447 | 10.093 |
| 2.007 | 19.808 |
| 3.623 | 39.177 |
| 2.249 | 21.739 |

# Totals
| user | cpu |
| ---- | ---- |
| 226.016 | 2537.312 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.763 | 120.824 |
