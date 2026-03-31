perf: initialize masked inpaint by bulk copy plus sparse overwrite

Rewrite `inpaint_mask` to first copy `original` into `inpainted` in one bulk pass, then iterate only over masked pixel indices gathered while building the highlight mask and overwrite those pixels with the seeded noise values. This preserves behavior but turns initialization for sparse clipped highlights from a branch-heavy full-image loop into mostly a contiguous copy plus sparse work.
