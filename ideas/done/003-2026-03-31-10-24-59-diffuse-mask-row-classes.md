perf: classify mask rows into clear full and mixed PDE fast paths

Build a tiny row-status table once from the boolean mask and dispatch three row kernels in `heat_PDE_diffusion`: clear rows do only the cheap reconstruction, full rows run a branchless masked PDE loop, and mixed rows keep the current per-pixel checks. The inpaint-highlights preset typically touches only part of the image, so this removes many mask loads and branches while preserving readable control flow.
outcome: not applicable

The target instance 19 has `luminance masking: 0.0`, which means `has_mask = FALSE` (line 2094: `const gboolean has_mask = (data->threshold > 0.f)`). When `has_mask` is false, every pixel gets `opacity = 1` (line 1080) and unconditionally runs the PDE — there is no mask to classify rows against. Building a row-status table would add pure overhead with zero benefit for this instance.

Additionally, the learnings from past experiments explicitly warn that mask-related restructuring attempts have been consistently negative: `mask-run-spans` (-7.8%), `outer-unswitch-has-mask` (-3.5%), and other sparse masked-path restructures were neutral to negative. The learnings say: "Avoid sparse masked-path restructures unless they delete substantial whole-image work."
