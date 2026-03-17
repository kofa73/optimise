Unroll the derivative accumulation loop

Unroll the derivative accumulation loop (`for k=0..3 { acc += derivatives[k]*ABCD[k] }`) into a single `for_each_channel` expression computing all 4 products in one pass. Eliminates outer loop overhead, removes zero-initialization, and lets GCC emit a single vectorized multiply-add chain.

outcome: not applicable

The derivative accumulation loop and the `derivatives` array have already been eliminated in a previous optimization. The convolutions are now computed and accumulated directly using `accumulate_convolution_direct`, which takes individual `ABCD[k]` values as parameters and accumulates the results straight into the `acc` variable, completely bypassing the need for an intermediate loop or array.
