eliminate `neighbour_pixel_HF[9]` and `neighbour_pixel_LF[9]` intermediate stack arrays entirely

Compute gradients, sums, and variance directly from HF/LF source pointers using pre-computed n0-n8 offsets. Avoids 72 float writes + reads from stack, leveraging L1 cache spatial locality.

outcome: not applicable

The optimization has already been applied. The intermediate stack arrays `neighbour_pixel_HF` and `neighbour_pixel_LF` are no longer present in the codebase. The gradients, sums, and variance are currently being computed directly from the `HF` and `LF` source pointers using the pre-computed `n0`-`n8` offsets, as requested in the optimization idea.
