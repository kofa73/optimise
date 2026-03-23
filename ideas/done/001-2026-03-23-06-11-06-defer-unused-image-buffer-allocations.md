perf: conditionally defer temporary image buffer allocations to when actually required

Currently, the full-image temporary buffers `temp1`, `temp2`, and `LF_even` are unconditionally allocated via `dt_iop_alloc_image_buffers` at the start of `process`. However, many fast-path presets (like `sharpness | fast` where `iterations == 1`, `scales == 1`, and `has_mask == false`) never use these buffers. `temp1` is only needed if `has_mask` is true or `iterations > 2`; `temp2` is only needed if `iterations > 1`; and `LF_even` is only needed if `scales > 1`. By conditionally allocating these buffers only when their respective conditions are met, we can save hundreds of megabytes of useless VMA allocations and reduce TLB tracking overhead for single-iteration pipelines.
outcome: target not reached: 186.585s vs baseline 186.625s (+0.0%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.733 | 61.139 |
| 10.602 | 116.170 |
| 8.972 | 97.143 |
| 9.956 | 98.934 |
| 10.046 | 100.201 |
| 10.271 | 116.520 |
| 9.895 | 113.600 |
| 10.113 | 115.323 |
| 9.883 | 105.191 |
| 10.001 | 113.134 |
| 9.781 | 110.650 |
| 9.325 | 105.675 |
| 6.627 | 69.480 |
| 9.685 | 106.152 |
| 9.850 | 105.802 |
| 6.706 | 73.686 |
| 6.660 | 74.825 |
| 6.649 | 71.623 |
| 8.081 | 91.179 |
| 9.344 | 107.086 |
| 8.405 | 93.962 |

# Totals
| user | cpu |
| ---- | ---- |
| 186.585 | 2047.475 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.885 | 97.499 |
