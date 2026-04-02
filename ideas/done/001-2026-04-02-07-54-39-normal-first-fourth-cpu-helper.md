perf: add a no-mask normal-preset CPU helper for matched first-and-fourth diffusion

Add a dedicated CPU path for the common “normal” shape used by instance 14: no mask, no luminance masking, zero sharpness, only 1st and 4th orders active, with matched speeds and matched anisotropy. Instead of entering the generic mixed-order machinery, dispatch to a helper that evaluates the shared conductance state once, applies only the two required stencil families, and skips all setup and per-pixel branching for disabled orders. This follows the preset-specific-helper pattern that has already paid off elsewhere, but targets the under-improved normal instance directly.
outcome: improvement
commit: 38cfd9bcd5
Reduced instance 14 time from 9.154s to 8.550s (+6.6% improvement), reduced sum(user) from 161.306s to 160.993s (~+0.2% improvement)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.691 | 61.546 |
| 9.392 | 106.213 |
| 7.255 | 80.654 |
| 9.322 | 102.866 |
| 9.268 | 103.386 |
| 9.158 | 104.214 |
| 8.769 | 101.487 |
| 8.987 | 103.498 |
| 0.040 | 0.259 |
| 9.902 | 111.936 |
| 9.597 | 110.422 |
| 9.176 | 104.319 |
| 6.400 | 69.024 |
| 9.688 | 108.132 |
| 8.550 | 94.585 |
| 5.423 | 59.830 |
| 5.425 | 61.001 |
| 6.433 | 69.302 |
| 7.225 | 82.224 |
| 8.410 | 96.706 |
| 6.882 | 76.135 |

# Totals
| user | cpu |
| ---- | ---- |
| 160.993 | 1807.739 |

# Averages
| user | cpu |
| ---- | ---- |
| 7.666 | 86.083 |
