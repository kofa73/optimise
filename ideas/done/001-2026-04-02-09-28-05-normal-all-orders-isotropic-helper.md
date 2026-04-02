perf: add no-mask zero-sharpness helper for the fully isotropic four-order normal path

Add a dedicated CPU helper for the exact hot family behind instance 18: no mask, `sharpness == 0`, `anisotropy == 1` for all active orders, and all first through fourth-order terms enabled. The existing fast paths cover narrower mixtures; this one should hardwire the active-order set, drop generic mixed-mode plumbing, remove per-pixel order dispatch, and keep only the scalar edge-sensitivity work that this preset actually needs. This is the most promising idea because past results show preset-specific helpers win when they delete substantial generic logic, and this instance is both under-optimized and iteration-heavy.
outcome: improvement
commit: 37c6f583ad
Reduced instance 18 time from 7.225s to 6.711s (+7.1% improvement), reduced sum(user) from 160.993s to 159.638s (~+0.8% improvement)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.684 | 61.612 |
| 9.463 | 105.888 |
| 7.239 | 80.292 |
| 9.266 | 103.391 |
| 9.298 | 103.098 |
| 9.054 | 103.536 |
| 8.729 | 100.946 |
| 8.921 | 102.776 |
| 0.040 | 0.241 |
| 9.813 | 112.100 |
| 9.642 | 109.658 |
| 9.125 | 104.559 |
| 6.436 | 68.564 |
| 9.616 | 108.085 |
| 8.525 | 94.318 |
| 5.511 | 60.451 |
| 5.532 | 61.646 |
| 6.399 | 69.713 |
| 6.711 | 75.332 |
| 7.780 | 88.771 |
| 6.854 | 76.366 |

# Totals
| user | cpu |
| ---- | ---- |
| 159.638 | 1791.343 |

# Averages
| user | cpu |
| ---- | ---- |
| 7.602 | 85.302 |
