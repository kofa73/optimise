eliminate `neighbour_pixel_HF[9]` and `neighbour_pixel_LF[9]` intermediate stack arrays entirely

Compute gradients, sums, and variance directly from HF/LF source pointers using pre-computed n0-n8 offsets. Avoids 72 float writes + reads from stack, leveraging L1 cache spatial locality.
