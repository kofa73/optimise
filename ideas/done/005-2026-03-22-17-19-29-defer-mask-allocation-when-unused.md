perf: defer mask buffer allocation to only when luminance threshold is active

Move the `dt_alloc_align_uint8(width * height)` mask allocation from the unconditional setup in `process()` to inside the `if(has_mask)` block, and pass NULL to `wavelets_process` when masking is inactive. Currently the mask buffer is always allocated even though the vast majority of presets have `threshold = 0` (no masking). For a 24MP image this wastes a 24MB allocation plus associated page table entries and TLB pressure. The allocation also participates in the `out_of_memory` check, meaning a spurious OOM from the unused mask buffer could abort processing. By deferring allocation, we eliminate one `posix_memalign` call, reduce peak memory, and avoid polluting the page tables with an untouched buffer in the common non-masking path.
outcome: target not reached: 188.403s vs baseline 188.886s (+0.3%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.888 | 62.978 |
| 10.727 | 119.164 |
| 9.099 | 101.481 |
| 10.112 | 110.807 |
| 10.045 | 111.491 |
| 10.322 | 117.702 |
| 9.904 | 113.224 |
| 10.060 | 115.305 |
| 9.893 | 110.881 |
| 10.053 | 113.515 |
| 9.809 | 111.211 |
| 9.331 | 105.681 |
| 6.715 | 71.312 |
| 9.822 | 108.882 |
| 9.973 | 110.449 |
| 6.762 | 74.779 |
| 6.777 | 76.272 |
| 6.716 | 72.086 |
| 8.244 | 92.967 |
| 9.553 | 109.313 |
| 8.598 | 95.451 |

# Totals
| user | cpu |
| ---- | ---- |
| 188.403 | 2104.951 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.972 | 100.236 |
