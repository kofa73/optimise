perf: specialize conductance setup for edge sensitivity 1 and threshold 1

Introduce a small helper for the common `edge_sensitivity == 1.0f` and `edge_threshold == 1.0f` case used by the normal instance, so the conductance setup can use simplified constants and avoid some generic parameter algebra around the anisotropic weighting path. This is not a fast-math rewrite of `dt_vector_exp`; it is a narrow constant-parameter specialization that reduces surrounding scalar work and live state while leaving the established vector exponential path untouched.
outcome: not applicable

The proposed specialization is stale against the current code and benchmark target. In [src/iop/diffuse.c](/workspace/darktable/src/iop/diffuse.c#L701), the `sharpness | normal` preset uses `.regularization = 2.94f` and `.variance_threshold = 0.0f`, and the CPU setup at [src/iop/diffuse.c](/workspace/darktable/src/iop/diffuse.c#L2942) still maps those through `powf(10.f, ...)`, so a fast path for raw parameters `1.0f/1.0f` would not be exercised by the stated hot instance. I made no changes.
