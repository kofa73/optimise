perf: collapse zero-speed diffusion orders into a compact active-order descriptor

Instead of carrying fixed four-slot parameter, tensor, and coefficient arrays through the CPU hot path, build a small descriptor list of active diffusion orders once per scale and pass that to shared `always_inline` helpers. On the target preset the list length is exactly one (fourth order only), which lets the compiler see a much smaller loop body, removes dead stack state for the zero-speed orders, and avoids repeated initialization of values that can never contribute.

outcome: not applicable

The optimization idea is based on an incorrect premise about the target instance and conflicts with the existing code structure.

**Why it doesn't apply:**

1. **The target instance has all four orders active**, not "exactly one (fourth order only)" as claimed. The speeds are: 1st=0.0065, 2nd=-0.25, 3rd=-0.25, 4th=-0.2774. None are zero, so no orders can be eliminated.

2. **The current code already eliminates dead orders via compile-time constant folding.** The 36-variant dispatch system (`FOR_EACH_DIFFUSE_ROW_LOOP`) passes `GRAD_ZERO`/`LAPL_ZERO`/`GRAD_MATCHED`/`LAPL_MATCHED` as compile-time constants to `diffuse_pixel_body`, which is `__attribute__((always_inline))`. The compiler removes all dead branches for zero orders at compile time. A runtime active-order descriptor list would be strictly worse because the compiler cannot constant-fold through a dynamically-sized loop.

3. **From the learnings, runtime-loop approaches over what is currently compile-time-specialized have consistently regressed** (e.g., "fuse-matched-gradient-and-laplacian-accumulations" -0.1%, "pair-4-compute_convolution_calls" -48.7%, "reduce-dispatch-instantiations-16-to-9" -0.1%). Replacing the current fixed-slot `ABCD[4]`/`isotropy_type[4]`/`half_anisotropy[4]` arrays with a runtime descriptor list of variable length would introduce dynamic indexing and remove the compile-time dead-code elimination that the dispatch system provides.
