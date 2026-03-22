perf: Reuse local center pixel arrays in final integration loop

The final solution update loop currently fetches `HF[index + c]` and `LF[index + c]` directly from global memory pointers. However, these exact memory addresses were already read and stored into the `HF_center` and `LF_center` aligned stack arrays during the initial neighbor extraction pass. By substituting the global memory fetches with the existing local `HF_center[c]` and `LF_center[c]` arrays, we eliminate redundant global L1 cache loads and force the compiler to reuse active vector registers populated earlier in the loop.
outcome: benchmark early abort: Benchmark early abort: 221.499s vs baseline 206.974s (-7.0%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.947 | 6.256 |
| 55.202 | 608.205 |
| 4.433 | 44.456 |
| 13.118 | 140.557 |
| 12.904 | 141.062 |
| 22.194 | 244.634 |
| 14.929 | 162.346 |
| 18.580 | 203.137 |
| 12.410 | 142.841 |
| 16.832 | 182.438 |
| 11.350 | 122.350 |
| 4.832 | 49.998 |
| 1.508 | 11.253 |
| 7.430 | 77.011 |
| 14.313 | 154.620 |
| 0.909 | 6.917 |
| 0.741 | 5.464 |
| 1.381 | 10.043 |
| 1.881 | 17.697 |
| 3.452 | 35.092 |
| 2.153 | 19.232 |

# Totals
| user | cpu |
| ---- | ---- |
| 221.499 | 2385.609 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.548 | 113.600 |
