perf: bypass zero-threshold edge clamp in anisotropic conductance setup

When the edge threshold is exactly zero, the conductance path no longer needs the threshold-subtract-and-clamp form before feeding the exponential; gradient-energy terms are already non-negative. Specialize that case so the hot anisotropic setup computes the exponent input directly from the accumulated norm, removing a compare/max sequence and associated dataflow from every pixel. This is narrowly targeted, readable, and especially relevant for the watercolor instance, which runs with threshold 0.0 on both active orders.
outcome: not applicable

The CPU anisotropic conductance setup in [`src/iop/diffuse.c`](/workspace/darktable/src/iop/diffuse.c) already feeds `dt_vector_exp()` from the raw non-negative gradient/laplacian norm (`sqrtf(gx² + gy²)` / `sqrtf(lx² + ly²)`) in the shared hot paths and the specialized CPU fast paths. There is no remaining threshold-subtract-and-clamp step on that conductance path to bypass, so this optimization has already effectively been applied.
