Replace nested coordinate permutation loops initializing `neighbour_pixel` matrix and calculating scalar variance with explicitly flattened sequential memory gathers.

Replace nested coordinate permutation loops initializing `neighbour_pixel` matrix and calculating scalar variance with explicitly flattened sequential memory gathers.
Outcome during previous experiment (with different test data): **SUCCESS**. Reduced baseline from 40.958s to 40.024s (~2.2% drop). Removed compiler bounds checks and inner iteration bloat.
