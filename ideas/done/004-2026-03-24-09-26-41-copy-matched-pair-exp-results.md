perf: copy dt_vector_exp results for matched gradient/laplacian order pairs via loop-invariant conditional

For the "sharpen demosaicing" preset, half_anisotropy[0]==half_anisotropy[2] and half_anisotropy[1]==half_anisotropy[3], meaning c2[0]==c2[2] and c2[1]==c2[3] at every pixel. After computing dt_vector_exp(c2[0]), the result can be memcpy'd to c2[2] instead of calling dt_vector_exp again. Similarly for c2[1]→c2[3]. This saves 2 dt_vector_exp calls per pixel. The key difference from the previously-failed "outer-loop unswitch matched anisotropy" (-17.1%) is the implementation: instead of duplicating the entire DIFFUSE_PIXEL_BODY macro, add a simple loop-invariant conditional copy inside the existing body. The condition (matched_grad_pair / matched_lapl_pair) is precomputed from function parameters before the pixel loop, so the branch predictor handles it perfectly with zero mispredictions. The copy is just 16 bytes (one dt_aligned_pixel_t) vs the ~20 integer operations of two dt_vector_exp calls, with no code duplication or icache bloat.
outcome: target not reached: 180.858s vs baseline 181.409s (+0.3%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.683 | 61.794 |
| 10.123 | 115.106 |
| 8.905 | 99.469 |
| 9.865 | 110.448 |
| 9.943 | 110.892 |
| 9.568 | 108.993 |
| 9.173 | 106.306 |
| 9.419 | 108.382 |
| 9.750 | 110.109 |
| 9.838 | 112.266 |
| 9.553 | 109.881 |
| 9.125 | 104.511 |
| 6.393 | 68.400 |
| 9.513 | 106.862 |
| 9.759 | 108.548 |
| 6.388 | 71.807 |
| 6.421 | 73.054 |
| 6.385 | 69.198 |
| 7.789 | 89.252 |
| 9.077 | 104.598 |
| 8.188 | 91.539 |

# Totals
| user | cpu |
| ---- | ---- |
| 180.858 | 2041.415 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.612 | 97.210 |
