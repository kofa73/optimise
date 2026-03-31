perf: specialize heat_PDE_diffusion for fourth-order-only masked inpaint

Add a dedicated CPU wrapper selected when `first == second == third == 0`, `sharpness == 0`, `regularization == 0`, and only `fourth` is active. That variant would compute only the HF laplacian orientation, only the 4th-order anisotropic kernel, and write `LF + HF + update` directly, instead of carrying four `c2` vectors, four kernels, four derivative accumulators, and generic accumulation code. This is a cleaner specialization than inner-loop order skipping because the compiler sees a single fixed algorithm.
outcome: not applicable

I can’t safely assess or apply the change under the current constraints because the only available workspace file-reading path here is via shell commands, which you explicitly prohibited, and no non-shell file/MCP resource access is available for [src/iop/diffuse.c](/workspace/darktable/src/iop/diffuse.c).
