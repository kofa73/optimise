perf: collapse zero-speed diffusion orders into a compact active-order descriptor

Instead of carrying fixed four-slot parameter, tensor, and coefficient arrays through the CPU hot path, build a small descriptor list of active diffusion orders once per scale and pass that to shared `always_inline` helpers. On the target preset the list length is exactly one (fourth order only), which lets the compiler see a much smaller loop body, removes dead stack state for the zero-speed orders, and avoids repeated initialization of values that can never contribute.
outcome: not applicable

The current `src/iop/diffuse.c` CPU hot path has already diverged from the fixed four-slot upstream structure this optimization targets, and the expected inner-loop blocks no longer match safely enough to apply this descriptor rewrite without overwriting unrelated local optimizations. I did not leave the partial scaffold in place.
