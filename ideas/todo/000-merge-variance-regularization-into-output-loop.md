Merge variance regularization (`variance[c] = threshold + variance[c] * factor`) into the output loop, computing `var` inline and eliminating a separate `for_each_channel` pass.

The output loop body stays small (1 FMA + division + add + fmax).
