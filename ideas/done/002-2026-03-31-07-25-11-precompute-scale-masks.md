perf: build scale-local luminance masks once and reuse them through PDE and reconstruction

Convert the luminance mask into per-scale mask buffers during the wavelet pyramid setup, then consume those scale-local masks directly in the PDE and reconstruction passes. Instance 8 pays for masking on every iteration, so replacing repeated full-resolution mask access and per-pixel scale adaptation with one precomputed mask per scale should reduce both bandwidth and scalar work while keeping the logic straightforward.

outcome: target not reached: 167.648s vs baseline 167.053s (-0.8%, need 3.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.642 | 61.252 |
| 9.492 | 105.653 |
| 9.126 | 102.514 |
| 9.284 | 102.444 |
| 9.231 | 102.464 |
| 9.085 | 103.743 |
| 8.754 | 100.815 |
| 8.941 | 102.881 |
| 0.040 | 0.244 |
| 9.855 | 111.310 |
| 9.572 | 109.880 |
| 9.132 | 104.146 |
| 6.438 | 69.069 |
| 9.684 | 108.449 |
| 9.948 | 110.785 |
| 5.885 | 65.536 |
| 5.919 | 66.580 |
| 6.443 | 69.672 |
| 8.165 | 93.324 |
| 9.518 | 109.841 |
| 7.494 | 83.365 |

# Totals
| user | cpu |
| ---- | ---- |
| 167.648 | 1883.967 |

# Averages
| user | cpu |
| ---- | ---- |
| 7.983 | 89.713 |
