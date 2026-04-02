perf: add a no-mask CPU helper for equal-speed equal-anisotropy four-order line drawing

Add a dedicated CPU fast path for the instance shape where there is no mask, `sharpness == 0`, `edge_threshold == 0`, and all four orders use the same speed and anisotropy. The helper should keep the existing traversal, but remove generic per-order branching and setup by computing one shared anisotropic conductance/tensor state per pixel and then applying the four order contributions through a compact fixed sequence. Past experiments show that targeted CPU helpers are one of the safest high-win patterns, and this instance is exactly the kind of repeated preset family that can justify one.
outcome: improvement
commit: 6de3c5f746
Reduced instance 1 time from 9.463s to 8.363s (+11.6% improvement), reduced sum(user) from 159.638s to 159.078s (~+0.4% improvement)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.712 | 62.035 |
| 8.363 | 92.810 |
| 7.262 | 80.636 |
| 9.279 | 103.522 |
| 9.328 | 103.331 |
| 9.113 | 104.399 |
| 8.769 | 101.306 |
| 8.991 | 103.328 |
| 0.040 | 0.255 |
| 9.883 | 112.362 |
| 9.638 | 110.851 |
| 9.173 | 104.988 |
| 6.449 | 69.078 |
| 9.652 | 108.528 |
| 8.573 | 94.191 |
| 5.487 | 60.952 |
| 5.537 | 61.234 |
| 6.417 | 69.826 |
| 6.736 | 75.334 |
| 7.786 | 88.970 |
| 6.890 | 76.569 |

# Totals
| user | cpu |
| ---- | ---- |
| 159.078 | 1784.505 |

# Averages
| user | cpu |
| ---- | ---- |
| 7.575 | 84.976 |
