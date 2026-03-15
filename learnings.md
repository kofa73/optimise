## What works
**Mathematical Simplifications:** Algebraic reductions that eliminate unnecessary operations without changing the result (e.g., removing `0.5f` scaling factors that cancel out later in angle ratios, computing `cos²θ`/`sin²θ` directly from gradients instead of computing angles first).
**Eliminating Intermediate Arrays:** Removing small stack-allocated arrays in favor of direct inline computation (e.g., stripping `kernel` matrices, eliminating `neighbour_pixel` arrays). This reduces stack memory traffic and register spilling.
**Judicious Loop Pairing/Unrolling:** Combining loops that do similar, independent work over the same dimensions (pairing `compute_convolution` calls, unrolling short derivative accumulation loops) helps vectorization and instruction-level parallelism.

## What to avoid
**Over-merging Loops:** Trying to fuse fundamentally different stages (e.g., merging gradient computation with sums/variance, or merging accumulation directly into output) consistently fails. This likely causes register spilling, breaks the compiler's auto-vectorizer, or destroys cache locality by requiring too many concurrent data streams.
**Conditional Branching in Inner Loops:** Adding `if` statements to skip work based on conditions (e.g., `has_mask=false`, conditional DCE, skipping isotropic branches) consistently fails. Branching destroys SIMD vectorization efficiency and pipeline predictability.
**Fast-Math/Precision Reductions:** Attempts to use lower-precision intrinsics (`dt_fast_inv_sqrtf`, `native_rsqrt`) or `#pragma GCC optimize("fast-math")` likely cause regression test failures due to the strict numerical precision required by the PDE diffusion mathematical model.
