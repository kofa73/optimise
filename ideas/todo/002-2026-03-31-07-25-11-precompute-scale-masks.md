perf: build scale-local luminance masks once and reuse them through PDE and reconstruction

Convert the luminance mask into per-scale mask buffers during the wavelet pyramid setup, then consume those scale-local masks directly in the PDE and reconstruction passes. Instance 8 pays for masking on every iteration, so replacing repeated full-resolution mask access and per-pixel scale adaptation with one precomputed mask per scale should reduce both bandwidth and scalar work while keeping the logic straightforward.
