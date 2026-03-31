perf: reuse per-scale dirty regions across masked diffuse iterations

Track a per-scale dirty region for the fixed inpaint mask and expand it by the stencil halo after each iteration, then recompute wavelet decomposition and PDE updates only inside those touched areas while reusing the previous iteration’s buffers elsewhere. For the “inpaint highlights” preset the mask is usually sparse but the iteration count is high, so avoiding full-frame recomputation across 33 passes should be far more valuable than shaving a few ALU ops inside the existing hot loop.

outcome: not applicable

The current CPU path already precomputes a per-scale sparse mask plan and reuses buffers outside those regions. More importantly, masked diffuse iterations only modify pixels where `mask[idx]` is true; outside the mask the PDE path is an identity passthrough and the caller preserves the untouched exterior. That means the dirty input set for every new iteration is the same fixed mask, so a per-iteration dirty-region tracker would collapse to the existing fixed per-scale halo regions rather than removing additional work.
