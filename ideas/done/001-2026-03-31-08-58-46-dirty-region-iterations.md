perf: reuse per-scale dirty regions across masked diffuse iterations

Track a per-scale dirty region for the fixed inpaint mask and expand it by the stencil halo after each iteration, then recompute wavelet decomposition and PDE updates only inside those touched areas while reusing the previous iteration’s buffers elsewhere. For the “inpaint highlights” preset the mask is usually sparse but the iteration count is high, so avoiding full-frame recomputation across 33 passes should be far more valuable than shaving a few ALU ops inside the existing hot loop.
outcome: not applicable

I can’t verify or implement this safely in the current session because your constraints forbid shell/file execution, and no non-shell file-access resource is available here to read `src/iop/diffuse.c`. Without inspecting the current CPU-path implementation first, I can’t determine applicability or make a compliant edit.
