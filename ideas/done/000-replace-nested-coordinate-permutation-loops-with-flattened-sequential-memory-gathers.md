Replace nested coordinate permutation loops initializing `neighbour_pixel` matrix and calculating scalar variance with explicitly flattened sequential memory gathers.

Replace nested coordinate permutation loops initializing `neighbour_pixel` matrix and calculating scalar variance with explicitly flattened sequential memory gathers.

outcome: not applicable

The optimization has already been applied. The code in `src/iop/diffuse.c` no longer uses a `neighbour_pixel` matrix or nested coordinate permutation loops. It already uses explicitly flattened sequential memory gathers (`n0` through `n8`) and calculates variance by directly summing the squared fetches (`sqf(hf0) + sqf(hf1) + ...`).
