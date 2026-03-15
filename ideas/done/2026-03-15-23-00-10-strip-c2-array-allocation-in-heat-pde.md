perf: Replace c2 array with scalar variables in heat_PDE_diffusion

Replace the `dt_aligned_pixel_t c2[4]` intermediate stack array inside the `heat_PDE_diffusion` innermost pixel loop with four independent `dt_aligned_pixel_t` variables (`c2_0`, `c2_1`, `c2_2`, `c2_3`), and manually unroll the `dt_vector_exp` loop. This avoids indexing into an array of vector types within the hot path, enabling the compiler to map these variables directly to AVX/SSE registers instead of spilling them to the stack. This directly applies the proven register-pressure reduction strategy that successfully yielded an ~11.9% improvement when stripping intermediate array allocations in `find_gradients` normalizations.
outcome: not applicable
