perf: use temporal stores for intermediate PDE scale outputs to preserve L3 cache hits

The PDE solver unconditionally uses nontemporal (streaming) stores for its output writes. While streaming stores are optimal for the final scale output (which is sent to the next module), outputs from intermediate wavelet scales are immediately consumed as inputs by the next finer scale (s-1) in the reconstruction loop. Using temporal stores for these intermediate scales allows the data to remain in the L2/L3 cache between scale passes (especially crucial during tiled processing), avoiding a full read-allocate round-trip to main memory and significantly improving memory bandwidth efficiency.
outcome: benchmark early abort: Benchmark early abort: 183.377s vs baseline 172.940s (-6.0%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 6.478 | 67.821 |
| 10.088 | 102.334 |
| 8.990 | 99.042 |
| 9.814 | 106.948 |
| 9.846 | 106.716 |
| 9.265 | 105.097 |
| 9.132 | 100.459 |
| 9.057 | 103.241 |
| 11.287 | 123.915 |
| 9.796 | 110.811 |
| 9.774 | 107.494 |
| 9.072 | 102.984 |
| 6.822 | 72.217 |
| 10.067 | 106.809 |
| 10.046 | 110.189 |
| 5.912 | 64.776 |
| 6.204 | 64.820 |
| 6.734 | 71.644 |
| 7.999 | 89.952 |
| 9.576 | 104.778 |
| 7.418 | 81.681 |

# Totals
| user | cpu |
| ---- | ---- |
| 183.377 | 2003.728 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.732 | 95.416 |
