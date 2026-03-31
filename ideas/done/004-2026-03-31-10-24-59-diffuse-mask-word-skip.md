perf: skip mixed-row clear regions a word at a time with packed mask words

Store the inpaint mask as packed `uint64_t` words and process mixed rows a word at a time. Zero words can take a tight `HF + LF` copy loop for 64 pixels, while non-zero words fall back to the existing pixel-wise PDE logic. This reduces mask bandwidth across many iterations and scales and avoids the extra indirection cost that made more general sparse-span approaches unattractive.
outcome: not applicable

Instance 19 (the priority target) has `luminance masking: 0.0`, which means `data->threshold = 0.0f` and therefore `has_mask = FALSE` (line 2094). The mask is never allocated, built, or consulted for this instance — the pixel body always takes the `opacity = 1` path.

Packing the inpaint mask into `uint64_t` words would add code complexity and memory management overhead with zero benefit for the no-mask case that dominates instance 19. Additionally, the learnings section explicitly warns against sparse masked-path restructures: `mask-run-spans` was -7.8%, `sparse-inpaint-initialization` was -0.1%, and similar approaches were consistently negative.
