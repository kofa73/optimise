perf: eliminate center pixel stack arrays by fetching directly from memory

The `LF_center` and `HF_center` stack arrays are currently used purely to cache the center pixel values (`lf4` and `hf4`) for the final accumulation pass. Because the underlying memory addresses (`LF + n4` and `HF + n4`) remain hot in the L1 cache from the immediately preceding gradient computations, we can omit these two intermediate stack arrays entirely. Passing the pointers directly to the accumulation function eliminates redundant local memory writes and reduces peak stack footprint.
outcome: benchmark early abort: Benchmark early abort: 222.093s vs baseline 217.223s (-2.2%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 0.902 | 6.248 |
| 56.748 | 657.045 |
| 4.565 | 47.394 |
| 12.862 | 142.882 |
| 13.039 | 142.379 |
| 21.966 | 250.937 |
| 14.404 | 166.770 |
| 18.350 | 208.559 |
| 12.579 | 137.773 |
| 16.270 | 188.184 |
| 11.268 | 124.529 |
| 4.682 | 51.166 |
| 1.468 | 11.403 |
| 7.661 | 79.222 |
| 14.485 | 164.099 |
| 0.912 | 7.177 |
| 0.725 | 5.505 |
| 1.332 | 10.053 |
| 1.939 | 19.036 |
| 3.775 | 36.571 |
| 2.161 | 20.717 |

# Totals
| user | cpu |
| ---- | ---- |
| 222.093 | 2477.649 |

# Averages
| user | cpu |
| ---- | ---- |
| 10.576 | 117.983 |
