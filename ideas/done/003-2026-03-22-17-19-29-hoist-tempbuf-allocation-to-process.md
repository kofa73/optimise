perf: hoist per-thread bspline tempbuf allocation from wavelets_process to process

Move the `dt_alloc_perthread_float(4 * width, &padded_size)` allocation from inside `wavelets_process()` to the `process()` function, passing `tempbuf` and `padded_size` as parameters. Currently this aligned per-thread buffer (~1.5MB for 16 threads at 6000px width) is allocated and freed on EVERY `wavelets_process()` call, which happens once per iteration. For multi-iteration presets (8-32 iterations for deblur/sharpen, up to 500 max), this means repeated `posix_memalign`/`free` system calls plus first-touch page fault overhead (~384 pages × 4μs each). The existing code even has a TODO comment acknowledging this: `//TODO: alloc in caller`. Hoisting the allocation eliminates `iterations - 1` unnecessary alloc/free cycles, following the proven "function-level guard" pattern of reducing per-call overhead.
outcome: target not reached: 188.249s vs baseline 188.886s (+0.3%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.880 | 63.094 |
| 10.729 | 118.127 |
| 9.066 | 101.288 |
| 10.108 | 110.895 |
| 10.067 | 111.677 |
| 10.378 | 117.112 |
| 9.902 | 113.083 |
| 10.044 | 115.278 |
| 9.878 | 110.710 |
| 9.978 | 113.230 |
| 9.797 | 110.937 |
| 9.296 | 105.672 |
| 6.725 | 71.543 |
| 9.758 | 108.678 |
| 9.982 | 110.416 |
| 6.812 | 74.857 |
| 6.768 | 76.100 |
| 6.715 | 72.460 |
| 8.220 | 92.960 |
| 9.557 | 108.825 |
| 8.589 | 95.552 |

# Totals
| user | cpu |
| ---- | ---- |
| 188.249 | 2102.494 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.964 | 100.119 |
