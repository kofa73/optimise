eliminate stack-allocated neighbor arrays via direct memory fetches

The inner loop currently gathers non-local pixels into 9-element `neighbour_pixel_HF` and `neighbour_pixel_LF` local arrays prior to calculation. These large upfront allocations (72 floats per pixel) cause heavy register spilling and stack memory traffic. Instead of doing a bulk block copy, we can fetch the specific pixels directly from the `HF` and `LF` pointers inline at the exact moments they are needed for the gradient stencils, variance accumulation, and symmetric convolutions. Relying on the L1 cache to handle these redundant localized reads is significantly faster than thrashing the stack with large intermediate arrays.

outcome: not applicable

The optimization has already been applied. The inner loop in `src/iop/diffuse.c` no longer allocates 9-element `neighbour_pixel_HF` or `neighbour_pixel_LF` arrays. Instead, it computes offsets (`n0` to `n8`) and directly fetches the specific pixels inline into individual scalar variables (`lf0` to `lf8` and `hf0` to `hf8`) exactly as described in the proposal.
