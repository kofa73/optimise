## What works
- **Replacing intermediate stack arrays with scalar variables:** Eliminating small array allocations within the innermost loops massively reduces register spilling and memory traffic (`strip-internal-array-allocations` gave ~11.9% improvement).
- **Exploiting mathematical symmetry to inline logic:** Leveraging spatial symmetries to inline convolutions algebraically instead of expanding arrays reduces multiply-accumulate operations and avoids intermediate allocations (`inline-symmetric-convolutions` gave ~11.7% improvement).
- **Compounding multiple near-miss optimizations:** Individually minor structural improvements (like inline accumulation or scalar memory offsets) can collectively cross performance thresholds when fused together (`compound-near-miss-optimizations` gave ~6.2% improvement).
- **Outer-loop unswitching for invariant conditions:** Evaluating conditions outside innermost loops safely skips heavy per-pixel math (e.g., bypassing math for isotropic orders) without introducing SIMD-breaking branches (`outer-loop-unswitch-isotropic-math` gave ~6.4% improvement).

## What to avoid
- **Inner-loop branching to skip work:** Adding conditional checks inside hot pixel loops (e.g., `skip-zero-speed-orders`, `copy-matched-anisotropy-c2-to-skip-expf`) breaks SIMD vectorization and causes overhead that negates the skipped work.
- **Merging sequential loops or independent passes:** Combining distinct loop bodies (like `pair-4-compute_convolution-calls` which regressed 48.7%, or `merge-variance-regularization-into-output-loop`) drastically increases register pressure and destroys instruction scheduling.
- **Altering floating-point accumulation order:** Refactoring math that changes the operation sequence (e.g., `fuse-paired-kernel-convolutions`) breaks floating-point bit-exactness and causes benchmark or QA test errors.
- **Minor mathematical micro-optimizations:** Trivial algebraic simplifications (removing 0.5f scaling, computing trigonometric functions directly from gradients) fail to overcome the real memory bounds, yielding insufficient or negligible gains.
- **Reordering execution without reducing allocations:** Swapping loop orders (`swap-sums-angle-loop-order`) or flattening permutation loops provides insufficient improvement if it doesn't solve underlying stack usage bottlenecks.
- **Code restructuring without operation reduction:** Fusing expressions or rewriting matrix initializations (`Fused-angle-ex`, `rewrite-9-element-kernel-matrix-instantiation`) often regresses performance by disrupting the compiler's existing optimizations.
