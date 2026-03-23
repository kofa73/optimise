perf: fuse build_mask and inpaint_mask into a single image pass for masking case

When `has_mask` is TRUE (luminance threshold > 0, used for inpainting presets), the code currently runs two separate full-image passes: `build_mask()` reads input and writes the boolean mask, then `inpaint_mask()` reads input AND mask and writes the inpainted buffer. These can be fused into a single pass that, for each pixel, computes the mask condition, writes the mask byte, and either copies the original pixel or generates inpainting noise — all without re-reading the input. This eliminates one complete image traversal (width × height × 4 floats of redundant input reads + width × height bytes of redundant mask reads), halving the I/O for the masking setup. The savings are proportional to image size and most impactful for inpainting presets (iterations=32) where setup overhead is a non-trivial fraction of total time.
outcome: target not reached: 187.896s vs baseline 188.886s (+0.5%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.847 | 62.924 |
| 10.729 | 118.554 |
| 9.088 | 101.289 |
| 10.114 | 110.860 |
| 10.055 | 111.592 |
| 10.326 | 116.537 |
| 9.898 | 113.103 |
| 10.049 | 115.161 |
| 9.878 | 110.774 |
| 9.954 | 113.215 |
| 9.786 | 110.935 |
| 9.297 | 105.609 |
| 6.728 | 71.410 |
| 9.776 | 108.589 |
| 9.953 | 110.225 |
| 6.740 | 74.740 |
| 6.741 | 75.515 |
| 6.733 | 72.516 |
| 8.174 | 92.064 |
| 9.494 | 108.285 |
| 8.536 | 94.988 |

# Totals
| user | cpu |
| ---- | ---- |
| 187.896 | 2098.885 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.947 | 99.947 |
