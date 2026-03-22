perf: Directly inline isotropic convolutions to bypass function overhead

When the macro flags `GRAD_ISOTROPIC` or `LAPL_ISOTROPIC` are true, the pixel solver currently still initializes zeroed dummy arrays and calls the generalized `accumulate_convolution_direct` function, which internally hits a runtime switch statement. By directly inlining the simple isotropic accumulation math into a compile-time `if (GRAD_ISOTROPIC)` branch inside the macro, we completely eliminate the function call boundary, dummy array instantiation, and switch branching for isotropic passes.
