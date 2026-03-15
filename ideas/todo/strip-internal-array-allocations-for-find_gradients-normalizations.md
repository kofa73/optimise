Strip internal array allocations for `find_gradients` normalizations

Strip internal array allocations for `find_gradients` normalizations, inlining arithmetic directly into native scalars inside `heat_PDE_diffusion`. Outcome during previous experiment (with different test data): **SUCCESS**. Reduced baseline from 45.631s to 40.958s (another ~10.2% drop).
