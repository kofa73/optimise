perf: free HF[s] buffers immediately after each scale's reconstruction to reduce peak memory and TLB pressure

Currently all HF[0..scales-1] buffers are allocated before processing and freed together afterward. During reconstruction (which processes scales from coarsest to finest), each HF[s] is used exactly once and never accessed again. By calling dt_free_align(HF[s]) immediately after scale s is reconstructed (and setting HF[s] = NULL), peak memory drops by approximately (scales-1) * width * height * 16 bytes. For a 10-scale 24MP image, this frees up to ~3.5GB earlier, reducing TLB pressure and virtual memory overhead. The change is trivial (one free call per scale in the reconstruction loop) and carries zero computational risk.
outcome: target not reached: 190.494s vs baseline 190.343s (-0.1%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.856 | 5.676 |
| 51.012 | 592.296 |
| 4.069 | 42.304 |
| 12.020 | 134.440 |
| 12.013 | 135.165 |
| 17.079 | 197.282 |
| 10.267 | 117.819 |
| 13.577 | 157.657 |
| 10.940 | 122.367 |
| 15.370 | 176.981 |
| 8.627 | 97.655 |
| 4.426 | 47.953 |
| 1.421 | 11.004 |
| 5.947 | 63.690 |
| 13.100 | 148.568 |
| 0.814 | 6.050 |
| 0.671 | 4.814 |
| 1.272 | 9.340 |
| 1.725 | 16.698 |
| 3.250 | 34.436 |
| 2.038 | 19.094 |

# Totals
| user | cpu |
| ---- | ---- |
| 190.494 | 2141.289 |

# Averages
| user | cpu |
| ---- | ---- |
| 9.071 | 101.966 |
