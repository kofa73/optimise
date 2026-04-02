perf: skip coarse CPU PDE scales whose update is provably sub-ulp for line drawing coefficients

Introduce a stricter CPU-only skip test based on the actual per-scale step size and the maximum possible stencil contribution for the active equal-speed line-drawing coefficients. The current negligible-scale logic appears to be norm-based; this idea instead asks whether an entire PDE pass can still change any output float at that scale. On large-radius presets, the coarse tail often survives generic checks while contributing less than float resolution, so deleting those whole-image passes should be more valuable than local ALU tuning.
outcome: target not reached: instance 12 improved from 6.449s to 6.401s (+0.7%, need 3.0%), overall sum(user) improved from 159.078s to 158.744s (+0.2%); failed gate: target threshold

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.687 | 61.389 |
| 8.326 | 93.314 |
| 7.243 | 80.344 |
| 9.319 | 102.906 |
| 9.293 | 103.399 |
| 9.163 | 103.790 |
| 8.753 | 101.311 |
| 8.971 | 103.347 |
| 0.040 | 0.249 |
| 9.873 | 112.128 |
| 9.567 | 109.878 |
| 9.192 | 104.534 |
| 6.401 | 69.028 |
| 9.693 | 108.389 |
| 8.570 | 94.052 |
| 5.491 | 60.850 |
| 5.507 | 61.898 |
| 6.420 | 69.197 |
| 6.640 | 75.272 |
| 7.739 | 88.536 |
| 6.856 | 76.177 |

# Totals
| user | cpu |
| ---- | ---- |
| 158.744 | 1779.988 |

# Averages
| user | cpu |
| ---- | ---- |
| 7.559 | 84.761 |
