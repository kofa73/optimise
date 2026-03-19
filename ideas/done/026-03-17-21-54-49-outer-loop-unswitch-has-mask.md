perf: Skip inner-loop opacity checks via outer-loop unswitching for has_mask

The `has_mask` boolean is a runtime invariant evaluated inside the innermost pixel loop to compute `opacity = (has_mask) ? mask[idx] : 1` and subsequently branch on `if(opacity)`. Because `has_mask` is derived dynamically at runtime, the compiler cannot automatically eliminate this inner-loop conditional or the associated array load (`mask[idx]`) for the common unmasked fast-path (`has_mask == false`), which disrupts optimal instruction scheduling and prevents straight-line auto-vectorization across adjacent pixels. By passing `has_mask` as a compile-time macro parameter (`HAS_MASK`) to `DIFFUSE_ROW_LOOP` and duplicating the macro invocations inside `heat_PDE_diffusion` via an outer `if(has_mask)` block, we can reliably force the compiler to strip out the `opacity` computation, the memory read, and the `else` branch entirely for the unmasked case, producing a perfectly linear sequence of unconditional math.
outcome: benchmark early abort: Benchmark early abort: 224.720s vs baseline 217.223s (-3.5%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.946 | 6.237 |
| 55.765 | 648.556 |
| 4.461 | 47.117 |
| 13.512 | 149.138 |
| 13.518 | 149.248 |
| 22.604 | 259.834 |
| 14.828 | 173.005 |
| 18.900 | 216.809 |
| 12.727 | 139.953 |
| 16.751 | 194.845 |
| 11.565 | 128.754 |
| 4.833 | 53.215 |
| 1.538 | 12.184 |
| 7.619 | 79.090 |
| 14.336 | 163.055 |
| 0.917 | 7.116 |
| 0.732 | 5.528 |
| 1.349 | 10.490 |
| 1.926 | 18.722 |
| 3.745 | 36.470 |
| 2.148 | 20.623 |

# Totals
| user | cpu |
| ---- | ---- |
| 224.720 | 2519.989 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.701 | 119.999 |
