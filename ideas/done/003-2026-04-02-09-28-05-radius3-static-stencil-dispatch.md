perf: specialize the CPU isotropic PDE path for the fixed radius-3 stencil

Dispatch a radius-3 helper that uses compile-time constant neighbor offsets, fixed row-pointer strides, and static coefficient tables instead of the generic radius-driven kernel setup and indexing. The target instance always uses `radius = 3`, so the generic radius machinery is pure overhead on its hot path. This keeps the traversal order intact while reducing inner-loop address arithmetic and enabling better constant folding in the isotropic convolution code without touching OpenCL.
outcome: not applicable

The current CPU PDE path in `src/iop/diffuse.c` already uses a fixed 3x3 stencil with compile-time neighbor layout (`n0`...`n8`) and row/column peeling, not a generic radius-driven isotropic kernel setup. The user `radius` parameter only affects wavelet scale weighting/selection, while the PDE solver itself operates on the fixed stencil with stride `mult`, so there is no remaining radius-3-specific generic indexing machinery to specialize without changing the algorithm beyond the requested idea.
