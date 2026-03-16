Unroll the derivative accumulation loop

Unroll the derivative accumulation loop (`for k=0..3 { acc += derivatives[k]*ABCD[k] }`) into a single `for_each_channel` expression computing all 4 products in one pass. Eliminates outer loop overhead, removes zero-initialization, and lets GCC emit a single vectorized multiply-add chain.
