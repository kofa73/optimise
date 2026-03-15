Rewrite the 9-element `kernel` matrix instantiation

Rewrite the 9-element `kernel` matrix instantiation with inline algebraically reduced scalar permutations (removing `compute_kernel` and `build_matrix` overheads). Outcome during previous experiment (with different test data): **SUCCESS**. Reduced baseline from 49.775s to 45.631s.
