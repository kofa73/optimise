perf: compute matched combinations directly to eliminate standalone LF/HF stack arrays

For fully matched passes, the code currently computes standalone symmetric pixel combination arrays for `LF` and `HF` independently in the initial neighbor-loading loop, only to iterate over them in a subsequent block to add them together into `combined` arrays. By evaluating the matched macro conditions directly within the initial neighbor-loading loop, we can compute the `combined` sums immediately (e.g., `combined_cross[c] = (lf08 - lf26) + (hf08 - hf26)`) and completely bypass allocating, storing, and fetching the intermediate standalone `LF` and `HF` arrays. This strictly halves the stack memory footprint for symmetric combinations and significantly reduces L1 cache traffic.
outcome: target not reached: 172.632s vs baseline 172.940s (+0.2%, need 1.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.606 | 60.531 |
| 9.122 | 103.289 |
| 8.767 | 97.463 |
| 9.175 | 102.708 |
| 9.138 | 102.177 |
| 8.902 | 101.466 |
| 8.557 | 98.997 |
| 8.843 | 100.396 |
| 9.730 | 110.112 |
| 9.652 | 110.584 |
| 9.457 | 108.621 |
| 8.949 | 102.752 |
| 6.337 | 67.602 |
| 9.221 | 103.701 |
| 9.498 | 106.515 |
| 5.736 | 63.475 |
| 5.734 | 64.798 |
| 6.279 | 68.185 |
| 7.759 | 87.116 |
| 8.937 | 103.191 |
| 7.233 | 81.095 |

# Totals
| user | cpu |
| ---- | ---- |
| 172.632 | 1944.774 |

# Averages
| user | cpu |
| ---- | ---- |
| 8.221 | 92.608 |
