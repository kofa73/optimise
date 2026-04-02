perf: reuse a shared primitive stencil basis across the four active anisotropic orders

Refactor the CPU hot loop so it computes a small basis of primitive symmetric neighbor sums once per pixel/channel, then forms each active order response from that basis instead of rebuilding equivalent axial/diagonal/mixed sums separately for each order. This is different from broad loop fusion: the traversal stays the same, but repeated arithmetic and live temporaries inside the per-pixel body shrink substantially. For the line-drawing instance, where all four orders are active together, this should reduce both ALU work and register pressure.
outcome: not applicable

`src/iop/diffuse.c` already computes and reuses shared symmetric stencil primitives per pixel/channel on the CPU path.

In the generic hot loop, [`src/iop/diffuse.c`](/workspace/darktable/src/iop/diffuse.c#L1129) materializes `LF_cross`, `LF_sum_corners`, `LF_sum_tb`, `LF_sum_lr`, `LF_center` and the corresponding HF basis once, then reuses them across the active orders via `accumulate_convolution_direct()` / `accumulate_isotropic()`. In the specialized equal-four-orders gradient fast path for the line-drawing preset family, [`src/iop/diffuse.c`](/workspace/darktable/src/iop/diffuse.c#L2292) already goes further: it computes the LF/HF directional basis once, merges them once with `combine_directional_stencils()`, and applies the fixed contribution sequence with two accumulation calls instead of rebuilding per-order sums. So the proposed optimization is already present in the current CPU code structure.
