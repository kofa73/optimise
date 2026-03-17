fully unroll the short derivative accumulation loop for vectorization

The final PDE update step contains a short `for(size_t k = 0; k < 4; k++)` loop to accumulate the 4 diffusion orders (`derivatives[k] * ABCD[k]`) into the `acc` array. Because these loop bounds are small, fixed, and structurally independent across the `k` dimension, manually unrolling this loop into a single combined statement allows the compiler's auto-vectorizer to issue the multiplication and addition instructions concurrently. This enhances instruction-level parallelism and completely removes loop control overhead, cleanly aligning with proven successes in unrolling short accumulation loops.
outcome: not applicable

The target `for(size_t k = 0; k < 4; k++)` loop for accumulating `derivatives[k] * ABCD[k]` into the `acc` array no longer exists in `src/iop/diffuse.c`. The code structure has evolved such that the convolution logic has been re-architected; it now directly accumulates into the `acc` array via four explicitly unrolled calls to an `accumulate_convolution_direct` function (one for each diffusion order), rendering this optimization either already applied or structurally obsolete.
