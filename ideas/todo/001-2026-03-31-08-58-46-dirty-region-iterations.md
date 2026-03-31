perf: reuse per-scale dirty regions across masked diffuse iterations

Track a per-scale dirty region for the fixed inpaint mask and expand it by the stencil halo after each iteration, then recompute wavelet decomposition and PDE updates only inside those touched areas while reusing the previous iteration’s buffers elsewhere. For the “inpaint highlights” preset the mask is usually sparse but the iteration count is high, so avoiding full-frame recomputation across 33 passes should be far more valuable than shaving a few ALU ops inside the existing hot loop.
