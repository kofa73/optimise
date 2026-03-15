## What works
- **Exploiting kernel/data symmetry to reduce operation count:** Identifying mathematical symmetries and using algebraic identities to eliminate large fractions of work. `inline-symmetric-convolutions` pre-combined symmetric neighbor pixels and reduced 36 multiplications to 16 per channel (~11.7% improvement).
- **Replacing intermediate arrays with scalar variables:** Removing small stack-allocated arrays in favor of direct inline scalar computation reduces memory traffic and register pressure. 
- **Inlining localized arithmetic:** `strip-internal-array-allocations` successfully inlined `find_gradients` normalizations into native scalars, yielding a ~11.9% improvement.
- **Preserving identical floating-point evaluation order:** Successful optimizations must be careful to produce bit-identical results by not reordering multiply-accumulate sequences. This is a strict prerequisite for passing benchmarks.

## What to avoid
- **Inlining non-local pixel access:** Eliminating stack-allocated neighbor arrays in favor of direct memory fetches causes obvious regressions (`inline-neighbor-pixel-access`). Bulk copying to stack arrays remains faster than repeated reads from L1 cache.
- **Over-merging loops:** Fusing fundamentally different computational stages causes register spilling, breaks auto-vectorization, or destroys cache locality.
- **Pairing independent function calls:** Grouping `compute_convolution` calls into fewer `for_each_channel` loops caused obvious regressions (`pair-4-compute_convolution-calls...`), likely due to increased loop overhead and register pressure.
- **Changing floating-point evaluation order:** Pre-combining or rearranging multiply-accumulate operations changes rounding sequences and causes benchmark errors. `fuse-paired-kernel-convolutions` failed by mathematically combining kernels before convolution.
- **Micro-optimizations that save minimal instructions:** Replacing simple arithmetic with mathematical identities (e.g., `simplify-b22-trace-identity` replacing addition with a trigonometric identity) caused obvious regressions by disrupting compiler instruction scheduling.
- **Restructuring code without algorithmic reduction:** Inlining matrix construction with algebraically reduced scalars (`rewrite-9-element-kernel-matrix-instantiation`) regressed on current workloads, suggesting it interfered with the compiler's auto-vectorization.
- **Conditional branching to skip work:** Adding conditionals to skip computations for zero-contribution orders (`skip-zero-speed-orders`) caused benchmark errors, as the altered code paths break bit-exact floating-point accumulation.
- **Fast-math/precision reductions:** Using lower-precision intrinsics or compiler flags like `-ffast-math` consistently causes regression test failures due to strict numerical precision requirements.
